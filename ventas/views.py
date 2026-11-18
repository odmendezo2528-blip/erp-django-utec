import io
from xhtml2pdf import pisa
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import DeleteView, DetailView, ListView

from .forms  import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta

# ── VISTAS DE LECTURA (W07) ──────────────────────────────────────────────

class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        return Venta.objects.select_related('cliente').prefetch_related('detalles__producto').order_by('-fecha')


class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'


# ── VISTAS DE ESCRITURA (W08) ────────────────────────────────────────────

@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    
    venta_form = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save()
            detalle = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(request, f'Venta #{venta.pk} registrada.')
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form,
    })


class VentaDeleteView(LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/eliminar.html'
    pk_url_kwarg = 'venta_id'
    success_url = reverse_lazy('ventas:lista')

    def form_valid(self, form):
        pk = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response


# ── GENERACIÓN DE PDF (W12) ──────────────────────────────────────────────

@login_required
def venta_pdf(request, venta_id):
    """Genera factura PDF usando xhtml2pdf."""
    venta = get_object_or_404(Venta.objects.select_related('cliente'), pk=venta_id)
    
    html_string = render_to_string('ventas/factura_pdf.html', {'venta': venta}, request=request)
    
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html_string), dest=result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{venta.pk:05d}.pdf"'
        return response
        
    return HttpResponse('Error al generar el PDF', status=500)