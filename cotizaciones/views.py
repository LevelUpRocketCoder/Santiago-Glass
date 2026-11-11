from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.template.loader import get_template
from decimal import Decimal
import json
import io
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .models import Cotizacion, ItemCotizacion, Producto
from clientes.models import Cliente

@login_required
def lista_cotizaciones(request):
    cotizaciones = Cotizacion.objects.select_related('cliente').all()
    return render(request, 'cotizaciones/lista.html', {'cotizaciones': cotizaciones})

@login_required
def nueva_cotizacion(request):
    clientes = Cliente.objects.filter(activo=True).order_by('nombre_completo')
    productos = Producto.objects.filter(activo=True).order_by('nombre')

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        fecha = request.POST.get('fecha')
        observaciones = request.POST.get('observaciones', '')
        items_json = request.POST.get('items_json', '[]')

        try:
            items_data = json.loads(items_json)
        except json.JSONDecodeError:
            messages.error(request, 'Error al procesar los Ã­tems.')
            return redirect('nueva_cotizacion')

        if not items_data:
            messages.error(request, 'Debe agregar al menos un Ã­tem a la cotizaciÃ³n.')
            return render(request, 'cotizaciones/form.html', {
                'clientes': clientes, 'productos': productos,
                'cliente_id': cliente_id, 'fecha': fecha, 'observaciones': observaciones,
            })

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        with transaction.atomic():
            cotizacion = Cotizacion(cliente=cliente, fecha=fecha, observaciones=observaciones)
            cotizacion.generar_numero()
            cotizacion.save()

            for item in items_data:
                prod = None
                if item.get('producto_id'):
                    try:
                        prod = Producto.objects.get(pk=item['producto_id'])
                    except Producto.DoesNotExist:
                        pass
                ItemCotizacion.objects.create(
                    cotizacion=cotizacion,
                    producto=prod,
                    descripcion=item['descripcion'],
                    color=item.get('color', ''),
                    detalles=item.get('detalles', ''),
                    unidad='m2',
                    cantidad=Decimal(str(item['cantidad'])),
                    precio_unitario=Decimal(str(item['precio'])),
                )
            cotizacion.calcular_total()

        messages.success(request, f'CotizaciÃ³n {cotizacion.numero} creada exitosamente.')
        return redirect('detalle_cotizacion', pk=cotizacion.pk)

    return render(request, 'cotizaciones/form.html', {
        'clientes': clientes,
        'productos': productos,
        'fecha_hoy': __import__('datetime').date.today().isoformat(),
    })

@login_required
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    items = cotizacion.items.all()
    return render(request, 'cotizaciones/detalle.html', {'cotizacion': cotizacion, 'items': items})

@login_required
def pdf_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    items = cotizacion.items.all()

    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img', 'logo.png')
    logo_path = logo_path.replace('\\', '/')

    item_count = items.count()
    empty_count = max(0, 5 - (item_count * 2))
    empty_rows = range(empty_count)

    template = get_template('cotizaciones/pdf.html')
    html = template.render({
        'cotizacion': cotizacion,
        'items': items,
        'logo_url': request.build_absolute_uri('/static/img/logo.jpg'),
        'total_letras': cotizacion.total_letras,
        'total_bs': cotizacion.total * getattr(cotizacion, 'tipo_cambio', 6.97),
        'c': cotizacion,
        'empty_rows': empty_rows,
        'request': request,
    })

    try:
        import weasyprint
        pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Cotizacion_{cotizacion.numero}.pdf"'
        return response
    except Exception:
        return HttpResponse(html)

@login_required
def word_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    items = cotizacion.items.all()

    document = Document()

    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)

    p = document.add_paragraph()
    run = p.add_run("SANTIAGO GLASS")
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(11, 20, 38)

    p_contact = document.add_paragraph()
    run_c = p_contact.add_run("Celular: 79142535   67064233 LA PAZ-BOLIVIA")
    run_c.font.size = Pt(9)
    run_c.font.color.rgb = RGBColor(245, 158, 11)
    run_c.bold = True

    document.add_paragraph(f"CLIENTE: {cotizacion.cliente.nombre_completo.upper()}")
    p_date = document.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_date = p_date.add_run(f"{cotizacion.fecha.strftime('%d/%m/%Y')}\n{cotizacion.numero}")
    run_date.font.size = Pt(10)

    table = document.add_table(rows=1, cols=6)
    table.style = 'Table Grid'

    hdr_cells = table.rows[0].cells
    headers = ['It', 'COTIZACION', 'UNIDAD', 'CANTIDAD', 'PR UNITARIO', 'COSTO']
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        for paragraph in hdr_cells[i].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9)
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), '111C2E')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    for idx, item in enumerate(items, 1):
        cat_row = table.add_row().cells
        cat_row[0].text = str(idx)
        prod_name = item.producto.nombre.upper() if item.producto else item.descripcion[:30].upper()
        cat_row[1].text = prod_name
        for paragraph in cat_row[1].paragraphs:
            for run in paragraph.runs:
                run.bold = True

        detail_row = table.add_row().cells
        detail_row[0].text = f"{idx}.1"
        desc_text = item.descripcion.upper()
        extras = []
        if item.color: extras.append(f"COLOR: {item.color.upper()}")
        if item.detalles: extras.append(f"TIPO: {item.detalles.upper()}")
        if extras:
            desc_text += "\n" + " | ".join(extras)
        detail_row[1].text = desc_text
        detail_row[2].text = "mÂ²"
        detail_row[3].text = str(item.cantidad)
        detail_row[4].text = f"{item.precio_unitario:,.0f}"
        detail_row[5].text = f"{item.total_item:,.0f}   Bs"

    tot_row = table.add_row().cells
    tot_row[0].merge(tot_row[2])
    tot_row[0].text = f"{cotizacion.total_letras}"
    tot_row[3].text = "BOLIVIANOS"
    tot_row[5].text = f"{cotizacion.total:,.0f}   Bs"
    for cell in [tot_row[0], tot_row[3], tot_row[5]]:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True

    p_nota = document.add_paragraph()
    run_nota = p_nota.add_run("\nESTA COTIZACION NO  INCLUYE FACTURA")
    run_nota.bold = True
    run_nota.font.size = Pt(10)

    if cotizacion.observaciones:
        document.add_paragraph(cotizacion.observaciones)

    document.add_paragraph("\n\n\n")
    p_sig2 = document.add_paragraph("ARQ.ERICK CHRISTIAN SILVA F. N-19454          TEC.CHRISTIAN SILVA L")
    for run in p_sig2.runs:
        run.bold = True
        run.font.size = Pt(9)

    f = io.BytesIO()
    document.save(f)
    f.seek(0)

    response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="Cotizacion_{cotizacion.numero}.docx"'
    return response

@login_required
def api_precio_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        'precio': str(producto.precio_unitario),
        'unidad': producto.unidad_medida,
        'descripcion': producto.descripcion or producto.nombre,
    })

@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'cotizaciones/productos.html', {'productos': productos})

@login_required
def nuevo_producto(request):
    from .forms import ProductoForm
    form = ProductoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto registrado.')
        return redirect('lista_productos')
    return render(request, 'cotizaciones/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
def editar_producto(request, pk):
    from .forms import ProductoForm
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('lista_productos')
    return render(request, 'cotizaciones/producto_form.html', {'form': form, 'titulo': 'Editar Producto'})


from django.http import HttpResponse, JsonResponse
from .dibujo_ventana import generar_svg

def api_dibujo_ventana(request):
    try:
        ancho = float(request.GET.get('ancho', 100))
        alto = float(request.GET.get('alto', 100))
        tipo = request.GET.get('tipo', 'ventana')
        estilo = request.GET.get('estilo', 'corrediza')
        rejilla = request.GET.get('rejilla', 'false') == 'true'
        color = request.GET.get('color', 'blanco')
        vidrio = request.GET.get('vidrio', 'simple')
        
        from .dibujo_ventana import generar_svg
        svg = generar_svg(ancho, alto, tipo, estilo, rejilla, color, vidrio)
        return HttpResponse(svg, content_type='image/svg+xml')
    except Exception as e:
        return HttpResponse(f"<svg><text y='20' fill='white'>Error: {str(e)}</text></svg>", content_type='image/svg+xml')

def diseno_wizard(request):
    return render(request, 'cotizaciones/diseno.html')
import re
from django.http import HttpResponse

import json
from django.http import JsonResponse, HttpResponse
from .dibujo_ia import generar_svg_ia
from .ai_parser import analizar_prompt_ia

def api_dibujo_ia(request):
    try:
        prompt = request.GET.get('prompt', '').lower()
        ancho = float(request.GET.get('ancho', 200))
        alto = float(request.GET.get('alto', 200))
        
        # 1. Extraer JSON simulando IA
        parametros = analizar_prompt_ia(prompt, ancho, alto)
        
        # 2. Generar el dibujo basado en los parametros (Punto 4)
        svg = generar_svg_ia(parametros)
        
        # 3. Retornar JSON (Punto 5)
        return JsonResponse({
            'svg': svg,
            'interpretacion': parametros['frase_interpretada'],
            'datos': parametros
        })
    except Exception as e:
        return JsonResponse({
            'svg': f"<svg><text y='20' fill='white'>Error: {str(e)}</text></svg>",
            'interpretacion': "Ocurrió un error al interpretar la solicitud."
        }, status=400)
