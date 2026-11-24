from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from clientes.models import Cliente
from productos.models import Producto
from configuracion.models import ConfiguracionERP


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente.nombre}"

    @property
    def total(self):
        return sum((detalle.subtotal for detalle in self.detalles.all()), Decimal('0.00'))


class DetalleVenta(models.Model):
    venta           = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad        = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Pedido(models.Model):
    """Modelo para los pedidos del e-commerce."""
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero_pedido = models.CharField(max_length=20, unique=True)
    cliente       = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    estado        = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total_pagado  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creado        = models.DateTimeField(auto_now_add=True)

    # ── CAMPO NUEVO DE LA W15 ──
    items_snapshot = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Snapshot de items del carrito',
        help_text='Copia del carrito al momento de crear el pedido.'
    )

    class Meta:
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering            = ['-creado']
  
    def __str__(self):
        return f"{self.numero_pedido} - {self.cliente.nombre}"