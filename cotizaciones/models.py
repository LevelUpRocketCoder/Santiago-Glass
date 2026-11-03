from django.db import models
from django.utils import timezone
from clientes.models import Cliente
from santiago_glass.utils import numero_a_letras

class Producto(models.Model):
    UNIDAD_CHOICES = [('m2', 'Metro cuadrado (m²)'), ('ml', 'Metro lineal (ml)'), ('pza', 'Pieza (pza)')]
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='m2')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()}) — Bs {self.precio_unitario}"


class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('emitida', 'Emitida'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    numero = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)
    obra = models.CharField(max_length=200, blank=True, null=True, verbose_name='Obra / Proyecto')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='emitida')
    observaciones = models.TextField(blank=True)
    tipo_cambio = models.DecimalField(max_digits=8, decimal_places=2, default=6.97, verbose_name='Tipo de cambio ($us 1 = Bs ?)')
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.numero} — {self.cliente.nombre_completo}"

    @property
    def total_letras(self):
        return numero_a_letras(self.total)

    def calcular_total(self):
        self.total = sum(item.total_item for item in self.items.all())
        self.save(update_fields=['total'])

    def generar_numero(self):
        year = timezone.now().year
        last = Cotizacion.objects.filter(numero__endswith=str(year)).order_by('-id').first()
        if last:
            try:
                last_num = int(last.numero.split('N°')[1].split('-')[0])
            except Exception:
                last_num = 0
        else:
            last_num = 0
        self.numero = f"N°{str(last_num + 1).zfill(4)}-{year}"


class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField()
    color = models.CharField(max_length=100, null=True, blank=True)
    detalles = models.CharField(max_length=100, null=True, blank=True)
    unidad = models.CharField(max_length=10, default='m2')
    cantidad = models.DecimalField(max_digits=10, decimal_places=4)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_item = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_item = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion[:40]} — Bs {self.total_item}"


class Abertura(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='aberturas', null=True, blank=True)
    ancho_cm = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    alto_cm = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_hojas = models.IntegerField(default=2)
    con_rejilla = models.BooleanField(default=False)
    color_aluminio = models.CharField(max_length=50, default='blanco')
    tipo_vidrio = models.CharField(max_length=50, default='simple')
    cantidad = models.IntegerField(default=1)
    precio_calculado = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"Abertura {self.ancho_cm}x{self.alto_cm}cm"
