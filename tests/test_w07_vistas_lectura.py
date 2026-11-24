"""Tests de vistas de lectura — W07.
Adaptados en W09 para incluir login (las vistas ahora requieren auth).
"""
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from clientes.models import Cliente
from productos.models import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models import Venta


class VistasLecturaTest(TestCase):
    def setUp(self):
        # Crear un usuario y loguearlo para que las vistas no redirijan
        self.user = User.objects.create_user('lector', password='pass')
        self.client.force_login(self.user)

        # Datos de prueba
        self.cat = Categoria.objects.create(nombre='Electrónica')
        self.prov = Proveedor.objects.create(nombre='Prov', correo='p@t.com')
        self.prod = Producto.objects.create(
            nombre='Laptop', precio=Decimal('1000.00'), stock=5,
            categoria=self.cat, proveedor=self.prov
        )
        self.cli = Cliente.objects.create(nombre='Cliente', correo='c@t.com')
        self.venta = Venta.objects.create(cliente=self.cli)

    def test_detalle_producto_http_200(self):
        r = self.client.get(reverse('productos:detalle', args=[self.prod.pk]))
        self.assertEqual(r.status_code, 200)

    def test_lista_clientes_http_200(self):
        r = self.client.get(reverse('clientes:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'clientes/lista.html')

    def test_lista_proveedores_http_200(self):
        r = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(r.status_code, 200)

    def test_lista_ventas_http_200(self):
        r = self.client.get(reverse('ventas:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ventas/lista.html')

    def test_detalle_venta_http_200(self):
        r = self.client.get(reverse('ventas:detalle', args=[self.venta.pk]))
        self.assertEqual(r.status_code, 200)