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


@login_required
def salida_articulos(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    items = cotizacion.items.all()

    # Determinar el color RAL predominante de la cotización
    color_raw = (items.first().color if items.exists() and items.first().color else 'blanco').lower()
    if 'blanco' in color_raw:
        ral_color = 'LACADO BLANCO - 9010'
    elif 'bronce' in color_raw:
        ral_color = 'BRONCE ANODIZADO - 8014'
    elif 'negro' in color_raw or 'antracita' in color_raw:
        ral_color = 'NEGRO MATE - 9005'
    elif 'mate' in color_raw or 'natural' in color_raw:
        ral_color = 'ANODIZADO MATE - 0'
    else:
        ral_color = 'LACADO BLANCO - 9010'

    # Calcular cantidades técnicas a partir de la cotización
    total_m2 = sum(float(it.cantidad) for it in items) if items else 4.0
    num_aberturas = max(1, items.count())
    
    ancho_prom = 1.60
    alto_prom = 1.40
    hojas_totales = num_aberturas * 2

    longitud_guia_sup = round(ancho_prom * num_aberturas * 2, 2)
    longitud_guia_inf = round(ancho_prom * num_aberturas * 2, 2)
    longitud_jambas = round(alto_prom * num_aberturas * 2, 2)
    longitud_felpa = round((ancho_prom * 2 + alto_prom * 2) * hojas_totales * 1.6, 2)
    longitud_goma = round((ancho_prom + alto_prom) * 2 * hojas_totales, 2)
    longitud_espuma = round(ancho_prom * num_aberturas * 4, 2)

    uds_cierres = num_aberturas * 2
    uds_deflectores = num_aberturas * 2
    uds_rodamientos = hojas_totales * 2

    articulos = [
        {
            'tipo': 'guia_sup',
            'uds': num_aberturas * 2,
            'codigo': '4639',
            'nombre': 'OK GUIA SUPERIOR "T.U."',
            'nota': 'Perfil superior riel doble reforzado',
            'ral_int': ral_color,
            'ral_ext': ral_color,
            'longitud': f"{longitud_guia_sup} m",
        },
        {
            'tipo': 'cierre',
            'uds': uds_cierres,
            'codigo': 'CI92',
            'nombre': 'Cierre embutido',
            'nota': 'Mecanismo caracol con traba',
            'ral_int': ral_color,
            'ral_ext': ral_color,
            'longitud': '0 m',
        },
        {
            'tipo': 'deflector',
            'uds': uds_deflectores,
            'codigo': 'DF4',
            'nombre': 'Deflector con trampilla',
            'nota': 'Tapa desagüe con válvula antiviento',
            'ral_int': ral_color,
            'ral_ext': ral_color,
            'longitud': '0 m',
        },
        {
            'tipo': 'felpa',
            'uds': 1,
            'codigo': 'FP75F',
            'nombre': 'Felpa 7x5 con lámina',
            'nota': 'Sellado hermético perimetral de hojas',
            'ral_int': 'SIN TRATAR - 0',
            'ral_ext': 'SIN TRATAR - 0',
            'longitud': f"{longitud_felpa} m",
        },
        {
            'tipo': 'goma',
            'uds': 1,
            'codigo': 'GO05',
            'nombre': 'Junta acristalamiento 05',
            'nota': 'Goma cuña EPDM de alta durabilidad',
            'ral_int': 'SIN TRATAR - 0',
            'ral_ext': 'SIN TRATAR - 0',
            'longitud': f"{longitud_goma} m",
        },
        {
            'tipo': 'espuma',
            'uds': 1,
            'codigo': 'JU92',
            'nombre': 'Junta espuma',
            'nota': 'Banda autoadhesiva de estanqueidad',
            'ral_int': 'SIN TRATAR - 0',
            'ral_ext': 'SIN TRATAR - 0',
            'longitud': f"{longitud_espuma} m",
        },
        {
            'tipo': 'rodamiento',
            'uds': uds_rodamientos,
            'codigo': 'KI701',
            'nombre': 'Kit ventana con rodamiento',
            'nota': 'Garruchas con rodamiento a bolas de acero',
            'ral_int': 'SIN TRATAR - 0',
            'ral_ext': 'SIN TRATAR - 0',
            'longitud': '0 m',
        },
    ]

    return render(request, 'cotizaciones/salida_articulos.html', {
        'cotizacion': cotizacion,
        'articulos': articulos,
    })


from .optimizador_vidrio import optimizar_planchas_vidrio
import re

def extraer_piezas_de_cotizacion(cotizacion):
    """Extrae las piezas de vidrio de una cotización para el optimizador."""
    piezas = []
    items = cotizacion.items.all()
    
    for idx, item in enumerate(items, 1):
        desc = item.descripcion
        cant = int(item.cantidad) if item.cantidad >= 1 else 1
        
        # Buscar medidas en la descripción (ej: 120x190 o 1.20 x 1.90 o 1200x1900)
        match = re.search(r'(\d+[\.,]?\d*)\s*[xX*]\s*(\d+[\.,]?\d*)', desc)
        if match:
            v1 = float(match.group(1).replace(',', '.'))
            v2 = float(match.group(2).replace(',', '.'))
            # Si están en metros, convertir a mm
            ancho_mm = v1 * 1000 if v1 < 10 else (v1 * 10 if v1 < 100 else v1)
            alto_mm = v2 * 1000 if v2 < 10 else (v2 * 10 if v2 < 100 else v2)
        else:
            # Estimación estándar basada en m2
            m2 = float(item.cantidad)
            ancho_mm = 1200.0
            alto_mm = round((m2 / 1.2) * 1000, 0) if m2 > 0 else 1000.0
            if alto_mm > 2400:
                alto_mm = 1800.0
                ancho_mm = round((m2 / 1.8) * 1000, 0)
        
        # Cada ventana corrediza típicamente se compone de 2 hojas de vidrio
        hoja_ancho = round(ancho_mm / 2 + 25, 0) # traslape de 25-30 mm
        hoja_alto = round(alto_mm - 50, 0)     # descuento de perfilería

        piezas.append({
            'label': f"It.{idx} Fija ({item.producto.nombre if item.producto else 'Vidrio'})",
            'ancho': hoja_ancho,
            'alto': hoja_alto,
            'cantidad': cant,
            'desc': f"{item.descripcion[:30]}"
        })
        piezas.append({
            'label': f"It.{idx} Móvil ({item.producto.nombre if item.producto else 'Vidrio'})",
            'ancho': hoja_ancho,
            'alto': hoja_alto,
            'cantidad': cant,
            'desc': f"{item.descripcion[:30]}"
        })

    if not piezas:
        # Piezas de ejemplo si la cotización no tiene ítems
        piezas = [
            {'label': 'Ventana V1-Fija', 'ancho': 1180, 'alto': 1350, 'cantidad': 2, 'desc': 'Vidrio 8mm'},
            {'label': 'Ventana V1-Móvil', 'ancho': 1180, 'alto': 1350, 'cantidad': 2, 'desc': 'Vidrio 8mm'},
            {'label': 'Box Baño Fijo', 'ancho': 600, 'alto': 1880, 'cantidad': 1, 'desc': 'Templado 8mm'},
            {'label': 'Box Baño Corredizo', 'ancho': 620, 'alto': 1880, 'cantidad': 1, 'desc': 'Templado 8mm'}
        ]
    return piezas

@login_required
def optimizador_vidrio(request):
    """Optimizador interactivo de planchas de vidrio 2D."""
    piezas_iniciales = [
        {'label': 'V1 - Paño Fijo', 'ancho': 1180, 'alto': 1350, 'cantidad': 2, 'desc': 'Vidrio Float 8mm'},
        {'label': 'V1 - Hoja Móvil', 'ancho': 1180, 'alto': 1350, 'cantidad': 2, 'desc': 'Vidrio Float 8mm'},
        {'label': 'Box Baño Fijo', 'ancho': 600, 'alto': 1880, 'cantidad': 1, 'desc': 'Templado Incoloro'},
        {'label': 'Box Baño Puerta', 'ancho': 620, 'alto': 1880, 'cantidad': 1, 'desc': 'Templado Incoloro'},
        {'label': 'Ventana Cocina', 'ancho': 550, 'alto': 780, 'cantidad': 2, 'desc': 'Simple 4mm'}
    ]
    
    ancho_plancha = 3600.0
    alto_plancha = 2400.0
    margen = 4.0
    permitir_rotacion = True

    resultado = optimizar_planchas_vidrio(
        piezas_iniciales,
        ancho_plancha=ancho_plancha,
        alto_plancha=alto_plancha,
        margen_corte=margen,
        permitir_rotacion=permitir_rotacion
    )

    return render(request, 'cotizaciones/optimizador_vidrio.html', {
        'resultado': resultado,
        'resultado_json': json.dumps(resultado),
        'piezas_json': json.dumps(piezas_iniciales),
        'ancho_plancha': ancho_plancha,
        'alto_plancha': alto_plancha,
        'margen': margen,
        'permitir_rotacion': permitir_rotacion,
        'cotizacion': None
    })

@login_required
def optimizador_vidrio_cotizacion(request, pk):
    """Optimizador precargado con los vidrios de una cotización específica."""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    piezas_cotiz = extraer_piezas_de_cotizacion(cotizacion)
    
    ancho_plancha = 3600.0
    alto_plancha = 2400.0
    margen = 4.0
    permitir_rotacion = True

    resultado = optimizar_planchas_vidrio(
        piezas_cotiz,
        ancho_plancha=ancho_plancha,
        alto_plancha=alto_plancha,
        margen_corte=margen,
        permitir_rotacion=permitir_rotacion
    )

    return render(request, 'cotizaciones/optimizador_vidrio.html', {
        'resultado': resultado,
        'resultado_json': json.dumps(resultado),
        'piezas_json': json.dumps(piezas_cotiz),
        'ancho_plancha': ancho_plancha,
        'alto_plancha': alto_plancha,
        'margen': margen,
        'permitir_rotacion': permitir_rotacion,
        'cotizacion': cotizacion
    })

@login_required
def api_optimizar_vidrio(request):
    """API AJAX para recalcular el plano de corte en tiempo real."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            piezas = data.get('piezas', [])
            ancho_plancha = float(data.get('ancho_plancha', 3600))
            alto_plancha = float(data.get('alto_plancha', 2400))
            margen = float(data.get('margen', 4))
            permitir_rotacion = bool(data.get('permitir_rotacion', True))

            resultado = optimizar_planchas_vidrio(
                piezas,
                ancho_plancha=ancho_plancha,
                alto_plancha=alto_plancha,
                margen_corte=margen,
                permitir_rotacion=permitir_rotacion
            )
            return JsonResponse({'status': 'ok', 'data': resultado})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
