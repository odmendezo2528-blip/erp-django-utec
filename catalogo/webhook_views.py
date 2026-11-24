import logging
import stripe
from django.conf import settings
from ventas.tasks import enviar_confirmacion_pedido
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from productos.models import Producto
from ventas.models import Pedido


logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse('Payload inválido.', status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse('Firma inválida.', status=400)

    tipo = event['type']
    if tipo == 'payment_intent.succeeded':
        _manejar_pago_exitoso(event['data']['object'])
    elif tipo == 'payment_intent.payment_failed':
        _manejar_pago_fallido(event['data']['object'])

    return HttpResponse(status=200)

def _manejar_pago_exitoso(payment_intent):
    """Procesa un pago confirmado por Stripe."""
    pedido_id = payment_intent.get('metadata', {}).get('pedido_id')
    if not pedido_id:
        logger.warning('Webhook: PaymentIntent sin pedido_id en metadata.')
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado en BD.')
        return

    if pedido.estado != 'pagado':
        pedido.estado = 'pagado'
        pedido.save(update_fields=['estado'])
        logger.info(f'Pedido {pedido.numero_pedido} actualizado a "pagado".')
        _descontar_stock(pedido)

        # ── NUEVO W16: Disparar la tarea asíncrona ──
        from ventas.tasks import enviar_confirmacion_pedido
        enviar_confirmacion_pedido.delay(pedido.pk)
    else:
        logger.info(f'Pedido {pedido.numero_pedido} ya estaba pagado — idempotente.')

def _manejar_pago_fallido(payment_intent):
    pedido_id = payment_intent.get('metadata', {}).get('pedido_id')
    if not pedido_id: return
    try:
        pedido = Pedido.objects.get(pk=pedido_id)
        if pedido.estado == 'pendiente':
            pedido.estado = 'cancelado'
            pedido.save(update_fields=['estado'])
    except Pedido.DoesNotExist:
        pass

def _descontar_stock(pedido):
    for item in (pedido.items_snapshot or []):
        prod_id = item.get('producto_id')
        cant = int(item.get('cantidad', 0))
        if prod_id and cant > 0:
            Producto.objects.filter(pk=prod_id, stock__gte=cant).update(stock=F('stock') - cant)