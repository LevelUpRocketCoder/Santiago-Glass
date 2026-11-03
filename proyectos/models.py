from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cotizaciones.models import Cotizacion

class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('cotizado', 'Cotizado'),
        ('aprobado', 'Aprobado'),
        ('en_instalacion', 'En Instalación'),
        ('entregado', 'Entregado'),
    ]
    cotizacion = models.OneToOneField(Cotizacion, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='aprobado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def dias_en_estado(self):
        return (timezone.now() - self.fecha_ultima_actualizacion).days

    @property
    def color_estado(self):
        colors = {'cotizado': 'secondary', 'aprobado': 'primary', 'en_instalacion': 'warning', 'entregado': 'success'}
        return colors.get(self.estado, 'secondary')

    def __str__(self):
        return f"Proyecto: {self.cotizacion.numero}"


class HistorialEstado(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    observacion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_cambio']
