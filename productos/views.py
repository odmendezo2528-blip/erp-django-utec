# productos/views.py
"""Vistas de la app productos — W07 y W08."""
import openpyxl
from openpyxl.styles import Font, PatternFill
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm


# --- VISTAS DE LECTURA (W07) ---

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        return (
            Producto.objects
            .select_related('categoria', 'proveedor')
            .filter(activo=True)
            .order_by('nombre')
        )


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg = 'producto_id'

    def get_queryset(self):
        return Producto.objects.select_related('categoria', 'proveedor')


# --- VISTAS DE ESCRITURA (W08) ---

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/crear.html'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg = 'producto_id'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" actualizado.'
        )
        return response


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/eliminar.html'
    pk_url_kwarg = 'producto_id'
    success_url = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'

    def form_valid(self, form):
        nombre = self.object.nombre
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return response

        import openpyxl
from openpyxl.styles import Font, PatternFill
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def exportar_excel(request):
    """Exporta el inventario de productos a un archivo Excel."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"

    # Encabezados
    headers = ['ID', 'Nombre', 'Precio', 'Stock', 'Categoría', 'Proveedor']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="0A2342", end_color="0A2342", fill_type="solid")

    # Datos
    for row, prod in enumerate(Producto.objects.all(), 2):
        ws.cell(row=row, column=1, value=prod.pk)
        ws.cell(row=row, column=2, value=prod.nombre)
        ws.cell(row=row, column=3, value=float(prod.precio))
        ws.cell(row=row, column=4, value=prod.stock)
        ws.cell(row=row, column=5, value=prod.categoria.nombre)
        ws.cell(row=row, column=6, value=prod.proveedor.nombre if prod.proveedor else "—")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inventario_erp.xlsx"'
    wb.save(response)
    return response