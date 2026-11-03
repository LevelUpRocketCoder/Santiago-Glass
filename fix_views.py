import re
with open('cotizaciones/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Borramos todo desde la primera definicion de api_dibujo_ventana hasta el final, y luego lo insertamos limpio
idx = text.find('def api_dibujo_ventana')
if idx != -1:
    text = text[:idx]

text += '''def api_dibujo_ventana(request):
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
'''

with open('cotizaciones/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
