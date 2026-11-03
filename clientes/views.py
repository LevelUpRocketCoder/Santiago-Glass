from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm

@login_required
def lista_clientes(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(nombre_completo__icontains=q) | clientes.filter(telefono__icontains=q)
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'q': q})

@login_required
def nuevo_cliente(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente registrado.')
        return redirect('lista_clientes')
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Nuevo Cliente'})

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado.')
        return redirect('lista_clientes')
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cotizaciones = cliente.cotizacion_set.all()
    return render(request, 'clientes/detalle.html', {'cliente': cliente, 'cotizaciones': cotizaciones})
