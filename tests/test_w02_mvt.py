"""Suite de pruebas W02 (Actualizada en W07) — Patrón MVT."""
from django.test import TestCase
from django.urls import reverse


class TemplatesRenderTest(TestCase):
    """Verifica que las vistas usan render() y los templates correctos."""

    def test_productos_usa_template_correcto(self):
        response = self.client.get(reverse('productos:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/lista.html')

    def test_clientes_usa_template_correcto(self):
        response = self.client.get(reverse('clientes:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/lista.html')

    def test_proveedores_usa_template_correcto(self):
        response = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/lista.html')

    def test_ventas_usa_template_correcto(self):
        response = self.client.get(reverse('ventas:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ventas/lista.html')