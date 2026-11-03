from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from cotizaciones.models import Cotizacion
from proyectos.models import Proyecto

@login_required
def dashboard(request):
    now = timezone.now()
    hora = now.hour
    if hora < 12:
        saludo = 'Buenos días'
    elif hora < 18:
        saludo = 'Buenas tardes'
    else:
        saludo = 'Buenas noches'

    total_cotizaciones = Cotizacion.objects.count()
    total_monto = Cotizacion.objects.aggregate(s=Sum('total'))['s'] or 0
    aprobadas = Cotizacion.objects.filter(estado='aprobada').count()
    proyectos_activos = Proyecto.objects.exclude(estado='entregado').count()

    # Revenue last 6 months
    meses_labels = []
    meses_data = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        if m <= 0:
            m += 12
            y -= 1
        meses_labels.append(f"{m}/{y}")
        total_mes = Cotizacion.objects.filter(fecha__year=y, fecha__month=m).aggregate(s=Sum('total'))['s'] or 0
        meses_data.append(float(total_mes))

    # Project status counts
    estados_labels = ['Cotizado', 'Aprobado', 'En Instalación', 'Entregado']
    estados_data = [
        Proyecto.objects.filter(estado='cotizado').count(),
        Proyecto.objects.filter(estado='aprobado').count(),
        Proyecto.objects.filter(estado='en_instalacion').count(),
        Proyecto.objects.filter(estado='entregado').count(),
    ]

    # Recent activity
    ultimas = Cotizacion.objects.select_related('cliente').order_by('-fecha_creacion')[:5]

    return render(request, 'reportes/dashboard.html', {
        'saludo': saludo,
        'usuario': request.user,
        'total_cotizaciones': total_cotizaciones,
        'total_monto': total_monto,
        'aprobadas': aprobadas,
        'proyectos_activos': proyectos_activos,
        'meses_labels': meses_labels,
        'meses_data': meses_data,
        'estados_labels': estados_labels,
        'estados_data': estados_data,
        'ultimas': ultimas,
    })

@login_required
def reporte(request):
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    estado = request.GET.get('estado', '')

    cotizaciones = Cotizacion.objects.select_related('cliente').all()
    if fecha_desde:
        cotizaciones = cotizaciones.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        cotizaciones = cotizaciones.filter(fecha__lte=fecha_hasta)
    if estado:
        cotizaciones = cotizaciones.filter(estado=estado)

    total_cantidad = cotizaciones.count()
    total_monto = cotizaciones.aggregate(s=Sum('total'))['s'] or 0

    return render(request, 'reportes/reporte.html', {
        'cotizaciones': cotizaciones,
        'total_cantidad': total_cantidad,
        'total_monto': total_monto,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estado': estado,
    })
