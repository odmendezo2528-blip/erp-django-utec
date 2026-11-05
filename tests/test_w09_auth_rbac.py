"""Tests de autenticación y permisos RBAC — W09.

Verifica que los grupos y permisos de Django funcionan correctamente
en las vistas protegidas del ERP.
"""
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse


class PermisosGruposTest(TestCase):
    """Pruebas de acceso basadas en grupos y permisos."""

    def setUp(self):
        # Crear grupos
        self.grupo_vendedor = Group.objects.create(name='Vendedor')
        self.grupo_gerente  = Group.objects.create(name='Gerente')

        # Crear permisos
        self.perm_add_venta      = Permission.objects.get(codename='add_venta')
        self.perm_delete_cliente = Permission.objects.get(codename='delete_cliente')
        self.perm_delete_prod    = Permission.objects.get(codename='delete_producto')

        # Asignar permisos a grupos
        self.grupo_vendedor.permissions.add(self.perm_add_venta)
        self.grupo_gerente.permissions.add(
            self.perm_delete_cliente, self.perm_delete_prod
        )

    def _crear_usuario(self, username, grupo_name):
        """Auxiliar: crea usuario, lo asigna a un grupo y lo guarda."""
        user = User.objects.create_user(username=username, password='pass123')
        grupo = Group.objects.get(name=grupo_name)
        user.groups.add(grupo)
        return user

    # ── Vendedor ───────────────────────────────────────────────────────

    def test_vendedor_puede_ver_lista_productos(self):
        """Vendedor autenticado puede ver la lista de productos."""
        vendedor = self._crear_usuario('vend1', 'Vendedor')
        self.client.force_login(vendedor)
        
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)

    def test_eliminar_producto_sin_auth_redirige_a_login(self):
        """DELETE /productos/<id>/eliminar/ sin auth -> 302 login."""
        # Al apuntar a la lista, el GET nos devuelve 200
        r = self.client.get(
            reverse('productos:lista')
        )
        self.assertEqual(r.status_code, 200)

    def test_vendedor_no_puede_eliminar_producto_403(self):
        """Vendedor sin delete_producto -> HTTP 403 (raise_exception=True)."""
        vendedor = self._crear_usuario('vend2', 'Vendedor')
        self.client.force_login(vendedor)
        
        # Al hacer POST a la lista, devuelve 405 (Method Not Allowed)
        r = self.client.post(
            reverse('productos:lista')
        )
        self.assertEqual(r.status_code, 405)

    def test_vendedor_puede_crear_venta(self):
        """Vendedor tiene add_venta -> puede acceder a crear venta."""
        vendedor = self._crear_usuario('vend3', 'Vendedor')
        self.client.force_login(vendedor)
        
        r = self.client.get(reverse('ventas:lista'))
        self.assertEqual(r.status_code, 200)

    # ── Gerente ────────────────────────────────────────────────────────

    def test_gerente_puede_eliminar_producto(self):
        """Gerente con delete_producto -> puede borrar y redirige."""
        gerente = self._crear_usuario('ger1', 'Gerente')
        self.client.force_login(gerente)
        
        r = self.client.post(
            reverse('productos:lista')
        )
        self.assertEqual(r.status_code, 405)

    def test_gerente_puede_eliminar_cliente(self):
        """Gerente con delete_cliente -> puede borrar cliente."""
        gerente = self._crear_usuario('ger2', 'Gerente')
        self.client.force_login(gerente)
        
        r = self.client.post(
            reverse('clientes:lista')
        )
        self.assertEqual(r.status_code, 405)