from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cotizaciones.models import Cotizacion
from .models import Proyecto, HistorialEstado

@login_required
def tablero(request):
    columnas = {}
    for val, label in Proyecto.ESTADO_CHOICES:
        columnas[val] = {'label': label, 'proyectos': Proyecto.objects.filter(estado=val).select_related('cotizacion__cliente')}
    return render(request, 'proyectos/tablero.html', {'columnas': columnas})

@login_required
def crear_proyecto(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    cotizacion.estado = 'aprobada'
    cotizacion.save(update_fields=['estado'])
    proyecto, created = Proyecto.objects.get_or_create(cotizacion=cotizacion)
    if created:
        HistorialEstado.objects.create(proyecto=proyecto, estado_anterior='emitida', estado_nuevo='aprobado', usuario=request.user)
        messages.success(request, 'Proyecto creado exitosamente.')
    return redirect('detalle_proyecto', pk=proyecto.pk)

@login_required
def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    historial = proyecto.historial.all()
    estados = Proyecto.ESTADO_CHOICES
    return render(request, 'proyectos/detalle.html', {'proyecto': proyecto, 'historial': historial, 'estados': estados})

@login_required
def cambiar_estado(request, pk):
    if request.method == 'POST':
        proyecto = get_object_or_404(Proyecto, pk=pk)
        nuevo_estado = request.POST.get('estado')
        observacion = request.POST.get('observacion', '')
        if nuevo_estado and nuevo_estado != proyecto.estado:
            HistorialEstado.objects.create(
                proyecto=proyecto,
                estado_anterior=proyecto.estado,
                estado_nuevo=nuevo_estado,
                observacion=observacion,
                usuario=request.user
            )
            proyecto.estado = nuevo_estado
            proyecto.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})
