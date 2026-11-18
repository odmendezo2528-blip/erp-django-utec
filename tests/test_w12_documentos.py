"""Tests W12 - Generación de PDF con xhtml2pdf (Entorno sin Docker)."""
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from clientes.models import Cliente
from productos.models import Categoria, Producto
from ventas.models import DetalleVenta, Venta

class VentaPDFTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pdfuser', password='pass')
        cat = Categoria.objects.create(nombre='Cat PDF')
        prod = Producto.objects.create(nombre='Prod PDF', precio=Decimal('500.00'), stock=5, categoria=cat)
        cli = Cliente.objects.create(nombre='Cliente PDF', correo='pdf@test.com')
        self.venta = Venta.objects.create(cliente=cli)
        DetalleVenta.objects.create(venta=self.venta, producto=prod, cantidad=2, precio_unitario=Decimal('500.00'))

    def test_pdf_sin_auth_redirige_a_login(self):
        r = self.client.get(reverse('ventas:pdf', args=[self.venta.pk]))
        self.assertEqual(r.status_code, 302)

    def test_pdf_con_auth_devuelve_200(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('ventas:pdf', args=[self.venta.pk]))
        self.assertEqual(r.status_code, 200)

    def test_pdf_content_type(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('ventas:pdf', args=[self.venta.pk]))
        self.assertIn('application/pdf', r.get('Content-Type', ''))

    def test_pdf_empieza_con_header_pdf(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('ventas:pdf', args=[self.venta.pk]))
        self.assertTrue(r.content[:4] == b'%PDF')

    def test_excel_exportacion_funciona(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('productos:exportar_excel'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r.get('Content-Type', ''))