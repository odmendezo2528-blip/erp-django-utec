"""Tareas asíncronas de la app ventas — W17 / W18."""
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

logger = logging.getLogger(__name__)

# ── TAREA 1: Confirmación de Pedido ──────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='ventas.enviar_confirmacion_pedido',
)
def enviar_confirmacion_pedido(self, pedido_id: int) -> dict:
    from configuracion.models import ConfiguracionERP
    from ventas.models        import Pedido

    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'[correo_confirmacion] Pedido {pedido_id} no existe.')
        return {'estado': 'error', 'razon': 'Pedido no encontrado'}

    if pedido.correo_enviado:
        logger.info(f'[correo_confirmacion] Pedido {pedido.numero_pedido}: correo ya enviado — skip.')
        return {'estado': 'skip', 'pedido_id': pedido_id, 'razon': 'correo ya enviado'}

    config = ConfiguracionERP.get_instance()
    items = pedido.items_snapshot or []
    url_pedido = f"https://erp-django-utec.onrender.com/ventas/{pedido.pk}/"

    contexto = {
        'pedido':     pedido,
        'config':     config,
        'items':      items,
        'url_pedido': url_pedido,
    }

    asunto      = f'Confirmación de pedido {pedido.numero_pedido} — {config.nombre_empresa}'
    texto_plano = render_to_string('emails/confirmacion_pedido.txt', contexto)
    html_body   = render_to_string('emails/confirmacion_pedido.html', contexto)

    correo_destino = pedido.cliente.correo
    correo_origen  = settings.DEFAULT_FROM_EMAIL

    mensaje = EmailMultiAlternatives(
        subject=asunto, body=texto_plano, from_email=correo_origen, to=[correo_destino]
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
        logger.info(f'[correo_confirmacion] Correo enviado a {correo_destino} para pedido {pedido.numero_pedido}.')
        pedido.correo_enviado = True
        pedido.save(update_fields=['correo_enviado'])
        return {'estado': 'ok', 'pedido_id': pedido_id, 'correo': correo_destino}
    except Exception as exc:
        logger.error(f'[correo_confirmacion] Error al enviar correo: {exc}')
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


# ── TAREA 2: Verificar Stock Bajo ────────────────────────────────────────

@shared_task(bind=True, max_retries=1, name='ventas.verificar_stock_bajo')
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    from productos.models import Producto

    productos_bajos = list(
        Producto.objects.select_related('categoria').filter(activo=True, stock__lt=umbral).values('pk', 'nombre', 'stock', 'categoria__nombre').order_by('stock')
    )

    if not productos_bajos:
        logger.info(f'[stock_bajo] Todos los productos tienen stock >= {umbral}. OK.')
        return {'umbral': umbral, 'total': 0, 'productos_bajos': []}

    logger.warning(f'[stock_bajo] {len(productos_bajos)} producto(s) con stock < {umbral}.')

    if settings.ADMINS:
        _enviar_alerta_stock(productos_bajos, umbral)

    return {'umbral': umbral, 'total': len(productos_bajos), 'productos_bajos': productos_bajos}


def _enviar_alerta_stock(productos_bajos: list, umbral: int) -> None:
    from configuracion.models import ConfiguracionERP

    config = ConfiguracionERP.get_instance()
    fecha  = timezone.now().strftime('%d/%m/%Y %H:%M')
    url_admin = 'https://erp-django-utec.onrender.com/admin/productos/producto/'

    contexto = {
        'productos_bajos': productos_bajos,
        'total_productos': len(productos_bajos),
        'umbral':          umbral,
        'fecha':           fecha,
        'url_admin':       url_admin,
        'config':          config,
    }

    asunto      = f'[ALERTA] {len(productos_bajos)} producto(s) con stock < {umbral}'
    texto_plano = render_to_string('emails/alerta_stock.txt',  contexto)
    html_body   = render_to_string('emails/alerta_stock.html', contexto)

    admin_nombre, admin_correo = settings.ADMINS[0]

    mensaje = EmailMultiAlternatives(
        subject=asunto, body=texto_plano, from_email=settings.DEFAULT_FROM_EMAIL, to=[admin_correo]
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
        logger.info(f'[stock_bajo] Alerta enviada a {admin_correo}. {len(productos_bajos)} productos.')
    except Exception as exc:
        logger.error(f'[stock_bajo] Error al enviar alerta: {exc}')


# ── TAREA 3: Reporte Diario de Ventas (W18) ──────────────────────────────

@shared_task(bind=True, name='ventas.reporte_ventas_diario')
def reporte_ventas_diario(self):
    from configuracion.models import ConfiguracionERP
    from ventas.models import Pedido, Venta

    hoy = timezone.localdate()
    config = ConfiguracionERP.get_instance()
    
    # Filtramos pedidos de hoy usando 'creado' (que es el campo que tiene tu modelo)
    pedidos_hoy = Pedido.objects.filter(creado__date=hoy, estado='pagado')
    
    total_pedidos = pedidos_hoy.count()
    total_facturado = pedidos_hoy.aggregate(total=Sum('total_pagado'))['total'] or Decimal('0.00')

    contexto = {
        'fecha': hoy.strftime('%d/%m/%Y'),
        'config': config,
        'total_pedidos': total_pedidos,
        'total_facturado': total_facturado,
        'top_productos': [], # Lo dejamos vacío por ahora para que no falle
        'url_admin': 'https://erp-django-utec.onrender.com/admin/',
    }

    asunto = f'Reporte de ventas del {contexto["fecha"]}'
    texto_plano = f"Pedidos hoy: {total_pedidos}\nTotal: ${total_facturado}"
    html_body = render_to_string('emails/reporte_ventas.html', contexto)

    if settings.ADMINS:
        admin_correo = settings.ADMINS[0][1]
        mensaje = EmailMultiAlternatives(
            subject=asunto, body=texto_plano, from_email=settings.DEFAULT_FROM_EMAIL, to=[admin_correo]
        )
        mensaje.attach_alternative(html_body, 'text/html')
        try:
            mensaje.send()
            logger.info(f'[reporte_diario] Reporte enviado a {admin_correo}.')
        except Exception as exc:
            logger.error(f'[reporte_diario] Error al enviar reporte: {exc}')

    return {
        'fecha': str(hoy),
        'total_pedidos': total_pedidos,
        'total_facturado': str(total_facturado),
        'top_productos': [],
    }