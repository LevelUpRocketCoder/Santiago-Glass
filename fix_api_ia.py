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
