import re

def analizar_prompt_ia(prompt, ancho_def=200, alto_def=200):
    prompt = prompt.lower()
    
    # 1. Tipo y Forma de Estructura
    tipo_estructura = 'ventana'
    forma = 'lineal'
    
    if 'puerta' in prompt: tipo_estructura = 'puerta'
    elif re.search(r'box|baño|ducha|esquinero|mampara|walk[- ]?in', prompt): 
        tipo_estructura = 'box_bano'
    elif 'vitrina' in prompt: tipo_estructura = 'vitrina'
    
    if re.search(r'esquinero|escuadra|en l\b', prompt): forma = 'esquinero'
    elif re.search(r'curvo|redondo|circular', prompt): forma = 'curvo'
    elif re.search(r'paño fijo|walk[- ]?in|panel fijo', prompt): forma = 'pano_fijo'
    elif re.search(r'frontal|entre paredes', prompt): forma = 'frontal'
    else: forma = 'frontal' if tipo_estructura == 'box_bano' else 'lineal'
    
    # 2. Apertura
    apertura = 'corrediza'
    if forma == 'pano_fijo': apertura = 'fija'
    elif 'batiente' in prompt or 'abrir' in prompt: apertura = 'batiente'
    elif re.search(r'\b(fija|estatica|quieta|entera)\b', prompt) and not re.search(r'\b(corrediz[oa]|movil|móvil|desliza)\b', prompt): 
        apertura = 'fija'
    elif 'guillotina' in prompt: apertura = 'guillotina'
    elif 'oscilobatiente' in prompt: apertura = 'oscilobatiente'
    
    # 3. Medidas
    ancho = ancho_def
    alto = alto_def
    profundidad = 0
    
    medidas_match = re.search(r'(\d+[\.,]?\d*)\s*(?:x|por)\s*(\d+[\.,]?\d*)(?:\s*(?:x|por)\s*(\d+[\.,]?\d*))?', prompt)
    if medidas_match:
        v1 = float(medidas_match.group(1).replace(',', '.'))
        v2 = float(medidas_match.group(2).replace(',', '.'))
        v1 = v1 * 100 if v1 <= 10 else v1
        v2 = v2 * 100 if v2 <= 10 else v2
        
        if medidas_match.group(3): # Ej: 90x90x190
            v3 = float(medidas_match.group(3).replace(',', '.'))
            v3 = v3 * 100 if v3 <= 10 else v3
            ancho, profundidad, alto = v1, v2, v3
            forma = 'esquinero'
        elif tipo_estructura == 'box_bano' and v1 < 140 and v2 < 140 and 'esquinero' in prompt:
            # Dijeron "90x90" asumiendo la base
            ancho = v1
            profundidad = v2
            alto = 190
        else:
            ancho = v1
            alto = v2

    # 4. Hojas y Distribución
    num_fijas = 0
    num_moviles = 0
    numero_hojas = 0
    
    fijas_match = re.search(r'(\d+|una|dos|tres|cuatro)\s*(?:hoja[s]?\s+|panel(?:es)?\s+|paño[s]?\s+)?(?:fija|estatica|quieta)', prompt)
    moviles_match = re.search(r'(\d+|una|dos|tres|cuatro)\s*(?:hoja[s]?\s+|panel(?:es)?\s+|paño[s]?\s+)?(?:movil|móvil|corrediz[oa]|puerta)', prompt)
    
    def parse_num(m):
        if not m: return 0
        txt = m.group(1)
        if txt == 'una': return 1
        if txt == 'dos': return 2
        if txt == 'tres': return 3
        if txt == 'cuatro': return 4
        return int(txt)

    num_fijas = parse_num(fijas_match)
    num_moviles = parse_num(moviles_match)
    total_mencionadas = num_fijas + num_moviles
    
    hojas_match = re.search(r'(\d+|una|dos|tres|cuatro)\s*hoja', prompt)
    if hojas_match:
        numero_hojas = parse_num(hojas_match)
    else:
        if total_mencionadas > 0:
            numero_hojas = total_mencionadas
        elif forma == 'pano_fijo':
            numero_hojas = 1
        elif forma == 'esquinero' and apertura == 'corrediza':
            numero_hojas = 4 # 2 fijas 2 moviles
        elif tipo_estructura == 'box_bano':
            numero_hojas = 2 # Frontal estándar
        else:
            numero_hojas = 2

    # Coherencia de listas
    hojas_list = []
    
    if total_mencionadas > 0:
        for _ in range(num_fijas): hojas_list.append({"tipo": "fija"})
        for _ in range(num_moviles): hojas_list.append({"tipo": "movil"})
    else:
        if forma == 'pano_fijo':
            hojas_list = [{"tipo": "fija"}]
        elif forma == 'esquinero' and numero_hojas == 4:
            hojas_list = [{"tipo": "fija"}, {"tipo": "movil"}, {"tipo": "movil"}, {"tipo": "fija"}]
        elif apertura == 'corrediza' and numero_hojas == 2:
            hojas_list = [{"tipo": "fija"}, {"tipo": "movil"}]
        elif apertura == 'corrediza' and numero_hojas == 4:
            hojas_list = [{"tipo": "fija"}, {"tipo": "movil"}, {"tipo": "movil"}, {"tipo": "fija"}]
        elif apertura == 'fija':
            hojas_list = [{"tipo": "fija"} for _ in range(numero_hojas)]
        else:
            for i in range(numero_hojas):
                hojas_list.append({"tipo": "movil" if i==0 else "fija"})

    # Re-evaluar numero total de hojas para asegurar que cuadra con la lista
    if len(hojas_list) > 0:
        numero_hojas = len(hojas_list)
        num_fijas = sum(1 for h in hojas_list if h['tipo'] == 'fija')
        num_moviles = sum(1 for h in hojas_list if h['tipo'] == 'movil')

    # 5. Serie de Aluminio y Tipo de Perfil
    serie_aluminio = 'serie_30'
    if re.search(r'serie\s*20|l[ií]nea\s*20|linea\s*20|s20', prompt):
        serie_aluminio = 'serie_20'
    elif re.search(r'serie\s*25|l[ií]nea\s*25|linea\s*25|s25', prompt):
        serie_aluminio = 'serie_25'
    elif re.search(r'serie\s*35|l[ií]nea\s*35|linea\s*35|s35', prompt):
        serie_aluminio = 'serie_35'
    elif re.search(r'serie\s*40|l[ií]nea\s*40|linea\s*40|serie\s*42|l[ií]nea\s*42|s40', prompt):
        serie_aluminio = 'serie_40'
    elif re.search(r'serie\s*60|l[ií]nea\s*60|serie\s*70|m[oó]dena|a30|herrer[oa]|dvh|rpt', prompt):
        serie_aluminio = 'serie_60'
    elif re.search(r'serie\s*80|l[ií]nea\s*80|muro\s*cortina|piel\s*de\s*vidrio|frente\s*integral', prompt):
        serie_aluminio = 'serie_80'
    elif re.search(r'tubo\s*3\s*x\s*1|tubular\s*3\s*x\s*1', prompt):
        serie_aluminio = 'tubo_3x1_5'
    elif re.search(r'tubo\s*2\s*x\s*1|tubular\s*2\s*x\s*1|tubo\s*50\s*x\s*25|2\s*x\s*1', prompt):
        serie_aluminio = 'tubo_2x1'
    elif re.search(r'tubo\s*1\s*x\s*1|tubular\s*1\s*x\s*1|tubo\s*25\s*x\s*25|1\s*x\s*1', prompt):
        serie_aluminio = 'tubo_1x1'
    elif 'tubo' in prompt or 'tubular' in prompt:
        serie_aluminio = 'tubo_2x1'
    elif re.search(r'perfil\s*u|canal\s*u|perfil\s*canal', prompt):
        serie_aluminio = 'perfil_u'
    elif tipo_estructura == 'puerta':
        serie_aluminio = 'serie_40'
    elif tipo_estructura == 'box_bano':
        serie_aluminio = 'serie_box'
    elif re.search(r'serie\s*30|l[ií]nea\s*30|linea\s*30|s30', prompt):
        serie_aluminio = 'serie_30'
        
    perfil_tipo = 'gancho' if apertura == 'corrediza' and numero_hojas >= 2 else 'estandar'
    if 'gancho' in prompt or 'traslape' in prompt:
        perfil_tipo = 'gancho'
    elif 'tubo' in prompt or 'tubular' in prompt:
        perfil_tipo = 'tubo'
    elif re.search(r'perfil\s*u|canal\s*u', prompt):
        perfil_tipo = 'perfil_u'
    elif re.search(r'[aá]ngulo|cantonera', prompt):
        perfil_tipo = 'angulo'

    # Marco y Color / Acabados
    marco = 'normal'
    color_aluminio = 'blanco'
    color_aluminio_nombre = 'Blanco Puro Electroestático (RAL 9016)'
    
    if 'sin marco' in prompt or (tipo_estructura == 'box_bano' and not re.search(r'perfil|marco', prompt)):
        marco = 'ninguno'
        color_aluminio = 'ninguno'
        color_aluminio_nombre = 'Sin Marco / Acero Inox'
    else:
        colores_map = [
            (['antracita', 'grafito', 'gris oscuro'], 'antracita', 'Gris Antracita Arquitectónico (RAL 7016)'),
            (['nogal', 'madera oscura'], 'madera', 'Sublimado Madera Nogal Americano'),
            (['roble', 'madera clara'], 'madera', 'Sublimado Madera Roble Natural'),
            (['cerezo', 'madera rojiza'], 'madera', 'Sublimado Madera Cerezo Cálido'),
            (['madera'], 'madera', 'Sublimado Efecto Madera Nogal'),
            (['oro', 'dorado'], 'oro', 'Dorado / Oro Anodizado'),
            (['champagne', 'champan'], 'champagne', 'Anodizado Champagne Claro'),
            (['titanio', 'plomo', 'inox', 'acero'], 'titanio', 'Titanio / Acero Inox Anodizado'),
            (['chocolate'], 'bronce', 'Marrón Chocolate Electroestático'),
            (['bronce', 'colonial'], 'bronce', 'Bronce Colonial Anodizado'),
            (['mate', 'natural', 'plata', 'anodizado'], 'mate', 'Anodizado Mate Natural (Plata 15µ)'),
            (['brillante', 'espejo', 'pulido'], 'brillante', 'Anodizado Brillante Pulido'),
            (['negro mate', 'negro microtexturado'], 'negro', 'Negro Mate Microtexturado (RAL 9005)'),
            (['negro'], 'negro', 'Negro Mate Microtexturado (RAL 9005)'),
            (['blanco brillante', 'blanco nieve'], 'blanco', 'Blanco Puro Electroestático (RAL 9016)'),
            (['blanco'], 'blanco', 'Blanco Puro Electroestático (RAL 9016)'),
            (['gris'], 'antracita', 'Gris Grafito (RAL 7024)')
        ]
        
        for triggers, c_id, c_nom in colores_map:
            if any(t in prompt for t in triggers):
                color_aluminio = c_id
                color_aluminio_nombre = c_nom
                marco = c_id
                break

    # 6. Tipo, Espesor, Composición y Acabado del Vidrio (Guía OnVentanas / ASTM / EN 1279)
    dvh_candidate = re.search(r'(\d{1,2})\s*[/xX\-]\s*(\d{1,2})\s*[/xX\-]\s*(\d{1,2})', prompt)
    dvh_match = None
    if dvh_candidate:
        v1_chk, vc_chk, v2_chk = int(dvh_candidate.group(1)), int(dvh_candidate.group(2)), int(dvh_candidate.group(3))
        if v1_chk <= 19 and vc_chk <= 28 and v2_chk <= 19:
            dvh_match = dvh_candidate

    lam_candidate = re.search(r'(\d{1,2})\s*\+\s*(\d{1,2})', prompt)
    lam_match = None
    if lam_candidate:
        l1_chk, l2_chk = int(lam_candidate.group(1)), int(lam_candidate.group(2))
        if l1_chk <= 19 and l2_chk <= 19:
            lam_match = lam_candidate
    
    espesor_vidrio_mm = 6
    composicion_vidrio = 'Monolítico 6 mm'
    camara_mm = 0
    espesor_total_vidrio_mm = 6.0
    
    tipo_vidrio = 'simple'
    if re.search(r'triple|3\s*c[aá]maras?', prompt):
        tipo_vidrio = 'triple'
        espesor_vidrio_mm = 4
        espesor_total_vidrio_mm = 12.0 # 4+4+4
        camara_mm = 12
        composicion_vidrio = 'Triple Vidrio Passivhaus 4/12/4/12/4 (Dos Cámaras Argón)'
    elif re.search(r'control\s*solar|guardian\s*sun|planistar|solar\s*control', prompt):
        tipo_vidrio = 'control_solar'
        espesor_vidrio_mm = 4
        espesor_total_vidrio_mm = 8.0 # 4+4
        camara_mm = 16
        composicion_vidrio = 'DVH 4/16/4 Control Solar Selectivo + Low-E'
    elif re.search(r'bajo\s*emisivo|baja\s*emisividad|low\s*[-eE]|t[eé]rmico|atr', prompt):
        tipo_vidrio = 'bajo_emisivo'
        espesor_vidrio_mm = 4
        espesor_total_vidrio_mm = 8.0
        camara_mm = 16
        composicion_vidrio = 'DVH 4/16/4 Bajo Emisivo Térmico (Low-E ATR)'
    elif re.search(r'ac[uú]stico|silence|antirruido|insonor', prompt):
        tipo_vidrio = 'acustico'
        espesor_vidrio_mm = 4
        espesor_total_vidrio_mm = 14.0 # 4+4 silence + 6mm
        camara_mm = 16
        composicion_vidrio = 'DVH Acústico 4+4 Silence / 16 / 6 mm'
    elif dvh_match or 'doble' in prompt or 'dvh' in prompt or 'cámara' in prompt or 'camara' in prompt:
        tipo_vidrio = 'doble'
        if dvh_match:
            p1, c, p2 = int(dvh_match.group(1)), int(dvh_match.group(2)), int(dvh_match.group(3))
            espesor_vidrio_mm = p1
            camara_mm = c
            espesor_total_vidrio_mm = float(p1 + p2)
            composicion_vidrio = f'DVH {p1}/{c}/{p2}'
        else:
            espesor_vidrio_mm = 4
            camara_mm = 16
            espesor_total_vidrio_mm = 8.0
            composicion_vidrio = 'DVH Estándar 4/16/4'
    def extraer_grosor_vidrio(p, default_val):
        m1 = re.search(r'(?:espesor|grosor)\s*(?:de\s*)?(\d{1,2})\s*(?:mm)?\b', p)
        if m1:
            v = int(m1.group(1))
            if 2 <= v <= 25: return v
        m2 = re.search(r'vidrio\s*(?:templado\s+|laminado\s+|simple\s+)?(?:de\s*)?(\d{1,2})\s*(?:mm)?\b', p)
        if m2:
            v = int(m2.group(1))
            if 2 <= v <= 25: return v
        m3 = re.search(r'\b(\d{1,2})\s*mm\b', p)
        if m3:
            v = int(m3.group(1))
            if 2 <= v <= 25: return v
        return default_val

    if lam_match or 'laminado' in prompt or 'laminar' in prompt or 'seguridad' in prompt:
        tipo_vidrio = 'laminado'
        if lam_match:
            l1, l2 = int(lam_match.group(1)), int(lam_match.group(2))
            espesor_vidrio_mm = l1 + l2
            espesor_total_vidrio_mm = float(l1 + l2)
            composicion_vidrio = f'Laminado de Seguridad {l1}+{l2} (con PVB)'
        else:
            g = extraer_grosor_vidrio(prompt, 6)
            espesor_vidrio_mm = g
            espesor_total_vidrio_mm = float(g)
            g1 = g // 2
            g2 = g - g1
            composicion_vidrio = f'Laminado de Seguridad {g1}+{g2} ({g} mm con PVB)'
    elif 'templado' in prompt or tipo_estructura == 'box_bano':
        tipo_vidrio = 'templado'
        espesor_vidrio_mm = extraer_grosor_vidrio(prompt, 8 if tipo_estructura == 'box_bano' else 6)
        espesor_total_vidrio_mm = float(espesor_vidrio_mm)
        composicion_vidrio = f'Templado de Seguridad {espesor_vidrio_mm} mm'
    else:
        tipo_vidrio = 'simple'
        espesor_vidrio_mm = extraer_grosor_vidrio(prompt, 6)
        espesor_total_vidrio_mm = float(espesor_vidrio_mm)
        composicion_vidrio = f'Monolítico Flotado {espesor_vidrio_mm} mm'
        
    acabado_vidrio = 'transparente'
    if re.search(r'esmerilado|arenado|pavonado|opaco', prompt): acabado_vidrio = 'esmerilado'
    elif re.search(r'bronce', prompt): acabado_vidrio = 'bronce'
    elif re.search(r'gris|humo', prompt): acabado_vidrio = 'gris'
    elif re.search(r'reflectivo|espej[oa]do|espejo', prompt): acabado_vidrio = 'reflectivo'
    elif re.search(r'catedral|corrugado|rayado', prompt): acabado_vidrio = 'catedral'

    # Extras
    rejilla = bool(re.search(r'rejilla|cuadricula|frances', prompt))
    mosquitero = bool(re.search(r'mosquitero|malla', prompt))

    # Construir frase limpia en español
    nombre_estructura = "Box de baño" if tipo_estructura == 'box_bano' else tipo_estructura.capitalize()
    
    hojas_desc = []
    if num_fijas > 0: hojas_desc.append(f"{num_fijas} fija{'s' if num_fijas>1 else ''}")
    if num_moviles > 0: hojas_desc.append(f"{num_moviles} móvil{'es' if num_moviles>1 else ''}")
    hojas_str = f"({', '.join(hojas_desc)})" if hojas_desc else f"({numero_hojas} hojas)"
    
    serie_display = {
        'serie_20': 'Serie 20 (Económica)',
        'serie_25': 'Serie 25 (Residencial)',
        'serie_30': 'Serie 30 (Estándar)',
        'serie_35': 'Serie 35 (Comercial)',
        'serie_40': 'Serie 40 (Reforzada)',
        'serie_60': 'Serie 60/Módena (Alta Gama)',
        'serie_80': 'Serie 80 (Muro Cortina)',
        'tubo_2x1': 'Tubo 2x1" (50x25 mm)',
        'tubo_1x1': 'Tubo 1x1" (25x25 mm)',
        'tubo_3x1_5': 'Tubo 3x1½"',
        'perfil_u': 'Perfil Canal U',
        'serie_box': 'Box Baño'
    }.get(serie_aluminio, 'Serie 30')
    
    if marco == 'ninguno':
        marco_str = "sin marco (accesorios inox)"
    else:
        marco_str = f"aluminio {serie_display} {color_aluminio_nombre}"
        if perfil_tipo == 'gancho': marco_str += " (con gancho traslape)"
        elif perfil_tipo == 'tubo': marco_str += " (perfil tubular)"
    
    frase = f"{nombre_estructura} {apertura} {hojas_str}, {ancho} x {alto} cm, vidrio {composicion_vidrio} {acabado_vidrio}, {marco_str}"
    
    if rejilla: frase += ", con rejilla"
    if mosquitero: frase += ", con mosquitero"

    resultado = {
        "tipo_estructura": tipo_estructura,
        "forma": forma,
        "apertura": apertura,
        "ancho_cm": ancho,
        "profundidad_cm": profundidad,
        "alto_cm": alto,
        "numero_hojas": numero_hojas,
        "hojas": hojas_list,
        "espesor_vidrio_mm": espesor_vidrio_mm,
        "espesor_total_vidrio_mm": espesor_total_vidrio_mm,
        "camara_mm": camara_mm,
        "composicion_vidrio": composicion_vidrio,
        "acabado_vidrio": acabado_vidrio,
        "marco": marco,
        "color_aluminio": color_aluminio,
        "color_aluminio_nombre": color_aluminio_nombre,
        "serie_aluminio": serie_aluminio,
        "serie_nombre": serie_display,
        "perfil_tipo": perfil_tipo,
        "tipo_vidrio": tipo_vidrio,
        "rejilla": rejilla,
        "mosquitero": mosquitero,
        "frase_interpretada": frase
    }
    
    # Cálculo de ingeniería estructural Dlubal / ASTM E1300, Física OnVentanas y Fijaciones
    ingenieria = calcular_ingenieria_y_herrajes(resultado)
    resultado["analisis_estructural"] = ingenieria["analisis_estructural"]
    resultado["despiece_herrajes"] = ingenieria["despiece_herrajes"]
    
    # Cálculo de despiece de perfiles y optimización de barras comerciales de 6m (Luminio)
    resultado["despiece_perfiles"] = calcular_despiece_perfiles(resultado)

    return resultado


import math

def calcular_ingenieria_y_herrajes(datos):
    ancho = float(datos.get('ancho_cm', 120))
    alto = float(datos.get('alto_cm', 190))
    tipo_est = datos.get('tipo_estructura', 'ventana')
    apertura = datos.get('apertura', 'corrediza')
    num_hojas = int(datos.get('numero_hojas', 2)) or 1
    espesor_mm = float(datos.get('espesor_vidrio_mm', 6))
    espesor_total_vidrio_mm = float(datos.get('espesor_total_vidrio_mm', espesor_mm))
    camara_mm = int(datos.get('camara_mm', 0))
    tipo_vidrio = datos.get('tipo_vidrio', 'simple')
    composicion_vidrio = datos.get('composicion_vidrio', f'{tipo_vidrio.capitalize()} {int(espesor_mm)} mm')
    marco = datos.get('marco', 'normal')
    hojas = datos.get('hojas', [])
    
    num_moviles = sum(1 for h in hojas if h.get('tipo') == 'movil')
    num_fijas = sum(1 for h in hojas if h.get('tipo') == 'fija')
    if num_moviles == 0 and apertura == 'corrediza':
        num_moviles = 1
        num_fijas = max(0, num_hojas - 1)
        
    forma = datos.get('forma', 'lineal')
    profundidad = float(datos.get('profundidad_cm', 0))
    ancho_desarrollo = (ancho + profundidad) if (forma == 'esquinero' and profundidad > 0) else ancho
    area_total_m2 = (ancho_desarrollo / 100.0) * (alto / 100.0)
    ancho_hoja = ancho_desarrollo / num_hojas
    area_hoja_m2 = (ancho_hoja / 100.0) * (alto / 100.0)
    
    # 1. CÁLCULO DE PESO DEL VIDRIO (Fórmula Técnica OnVentanas: Área m² x Espesor total vidrio mm x 2.5 kg/m²/mm)
    peso_total_vidrio_kg = round(area_total_m2 * espesor_total_vidrio_mm * 2.5, 2)
    peso_hoja_vidrio_kg = round(peso_total_vidrio_kg / num_hojas, 2)
    
    # 2. PROPIEDADES TÉRMICAS, ACÚSTICAS Y ENERGÉTICAS (Normas EN 673 / EN 410 / OnVentanas)
    props_map = {
        'simple': {
            'nombre_tecnico': 'Vidrio Monolítico Flotado',
            'ug_termico': 5.7,
            'aislamiento_acustico_db': 29 if espesor_mm <= 4 else (32 if espesor_mm <= 6 else 35),
            'factor_solar_g': 82,
            'transmision_luz_pct': 89,
            'clase_energetica': 'Clase F (Bajo aislamiento)',
            'ahorro_energia_pct': 0,
            'seguridad_humana': 'Estándar (Rotura en astillas grandes)'
        },
        'templado': {
            'nombre_tecnico': 'Vidrio Templado Térmico (Securit)',
            'ug_termico': 5.6,
            'aislamiento_acustico_db': 32 if espesor_mm <= 6 else (35 if espesor_mm <= 8 else 37),
            'factor_solar_g': 80,
            'transmision_luz_pct': 88,
            'clase_energetica': 'Clase E',
            'ahorro_energia_pct': 2,
            'seguridad_humana': 'Clase 1C1 (Seguridad: granos diminutos)'
        },
        'laminado': {
            'nombre_tecnico': 'Vidrio Laminado de Seguridad (con PVB)',
            'ug_termico': 5.3,
            'aislamiento_acustico_db': 35 if espesor_total_vidrio_mm <= 6 else 38,
            'factor_solar_g': 75,
            'transmision_luz_pct': 86,
            'clase_energetica': 'Clase E+',
            'ahorro_energia_pct': 7,
            'seguridad_humana': 'Clase 1B1 (Anticaída: retenido en lámina)'
        },
        'doble': {
            'nombre_tecnico': f'Doble Acristalamiento con Cámara ({camara_mm or 16} mm)',
            'ug_termico': 2.7 if camara_mm >= 16 else 2.8,
            'aislamiento_acustico_db': 31,
            'factor_solar_g': 76,
            'transmision_luz_pct': 80,
            'clase_energetica': 'Clase C (Buen Aislamiento)',
            'ahorro_energia_pct': 52,
            'seguridad_humana': 'Media (Cámara estanca)'
        },
        'bajo_emisivo': {
            'nombre_tecnico': 'DVH Bajo Emisivo Térmico (Low-E ATR con Plata)',
            'ug_termico': 1.3,
            'aislamiento_acustico_db': 32,
            'factor_solar_g': 60,
            'transmision_luz_pct': 75,
            'clase_energetica': 'Clase A (Alto Aislamiento Térmico)',
            'ahorro_energia_pct': 75,
            'seguridad_humana': 'Media-Alta'
        },
        'control_solar': {
            'nombre_tecnico': 'DVH Control Solar Selectivo + Low-E (Guardian Sun)',
            'ug_termico': 1.1,
            'aislamiento_acustico_db': 33,
            'factor_solar_g': 38,
            'transmision_luz_pct': 68,
            'clase_energetica': 'Clase A+ (Bloquea calor solar en verano)',
            'ahorro_energia_pct': 80,
            'seguridad_humana': 'Alta'
        },
        'acustico': {
            'nombre_tecnico': 'DVH Acústico Silence (PVB Acústico Asimétrico)',
            'ug_termico': 1.2,
            'aislamiento_acustico_db': 42,
            'factor_solar_g': 55,
            'transmision_luz_pct': 72,
            'clase_energetica': 'Clase A (Máximo Confort Antirruido)',
            'ahorro_energia_pct': 78,
            'seguridad_humana': 'Clase 1B1 Antirrobo & Acústica'
        },
        'triple': {
            'nombre_tecnico': 'Triple Acristalamiento Passivhaus (Dos Cámaras Argón)',
            'ug_termico': 0.6,
            'aislamiento_acustico_db': 38,
            'factor_solar_g': 50,
            'transmision_luz_pct': 70,
            'clase_energetica': 'Clase A++ (Estándar Passivhaus ECCN)',
            'ahorro_energia_pct': 89,
            'seguridad_humana': 'Máxima'
        }
    }
    propiedades_vidrio = props_map.get(tipo_vidrio, props_map['simple'])
    
    # 3. CÁLCULO ESTRUCTURAL (Criterio Dlubal / ASTM E1300 / DIN 18008)
    resistencia_factor = {
        'simple': 1.0,
        'laminado': 1.5,
        'doble': 2.0,
        'bajo_emisivo': 2.0,
        'control_solar': 2.0,
        'acustico': 2.5,
        'triple': 3.0,
        'templado': 4.5
    }.get(tipo_vidrio, 1.0)
    
    dim_menor_m = min(ancho_hoja, alto) / 100.0
    
    espesor_min_sugerido = 4
    if tipo_est == 'box_bano':
        if alto >= 180 or area_total_m2 >= 1.6:
            espesor_min_sugerido = 8
        else:
            espesor_min_sugerido = 6
    else:
        if area_hoja_m2 <= 0.8:
            espesor_min_sugerido = 4
        elif area_hoja_m2 <= 1.5:
            espesor_min_sugerido = 6 if tipo_vidrio == 'simple' else 4
        elif area_hoja_m2 <= 2.5:
            espesor_min_sugerido = 8 if tipo_vidrio == 'simple' else 6
        elif area_hoja_m2 <= 3.8:
            espesor_min_sugerido = 10 if tipo_vidrio == 'simple' else 8
        else:
            espesor_min_sugerido = 12 if tipo_vidrio == 'simple' else 10

    # Flecha estimada bajo presión de viento moderada-fuerte (0.6 kPa)
    flecha_aprox_mm = round((0.0035 * (dim_menor_m ** 4) * 1e9) / (70000 * (max(espesor_total_vidrio_mm, 2) ** 3) * resistencia_factor), 1)
    flecha_admisible_mm = round((dim_menor_m * 1000) / 150, 1) # L/150
    
    estado = 'optimo'
    color_estado = '#10b981' # verde
    titulo_estado = 'Seguridad Estructural Óptima'
    advertencia = ''
    
    if tipo_est == 'box_bano' and tipo_vidrio == 'simple':
        estado = 'peligro'
        color_estado = '#ef4444'
        titulo_estado = 'Riesgo: Vidrio No Apto Para Baño'
        advertencia = 'Norma de seguridad humana (OnVentanas / CTE): Los boxes de ducha exigen vidrio TEMPLADO o LAMINADO para evitar cortes graves por rotura.'
    elif espesor_total_vidrio_mm < espesor_min_sugerido:
        estado = 'peligro'
        color_estado = '#ef4444'
        titulo_estado = 'Riesgo: Espesor Insuficiente'
        advertencia = f'Para {round(area_hoja_m2, 2)} m² por hoja, {int(espesor_total_vidrio_mm)} mm puede quebrar por flexión ante presión de viento. Se recomienda mínimo {espesor_min_sugerido} mm.'
    elif espesor_total_vidrio_mm == espesor_min_sugerido and flecha_aprox_mm > (flecha_admisible_mm * 0.85):
        estado = 'limite'
        color_estado = '#f59e0b'
        titulo_estado = 'Al Límite de Deflexión'
        advertencia = f'El espesor cumple, pero se aconseja templado o subir a {espesor_min_sugerido+2} mm si estará en pisos altos o expuesto a viento fuerte.'
    else:
        advertencia = f'{composicion_vidrio} verificado. Flecha estimada {flecha_aprox_mm} mm (dentro del límite admisible L/150 = {flecha_admisible_mm} mm).'

    viento_max_kmh = round(math.sqrt(resistencia_factor * (max(espesor_total_vidrio_mm, 2) / 6.0) ** 2) * 115)
    
    # 4. CÁLCULO DE FIJACIONES, TORNILLOS Y HERRAJES
    is_sin_marco = marco == 'ninguno' or (tipo_est == 'box_bano' and marco != 'normal')
    
    pasos_w = max(2, math.ceil(ancho / 35.0))
    pasos_h = max(2, math.ceil(alto / 35.0))
    
    if is_sin_marco:
        tornillos_muro = pasos_h * 2 + 4
        tornillos_armado = 4
    else:
        tornillos_muro = (pasos_w + pasos_h) * 2
        tornillos_armado = 8 + (8 * num_hojas)
        
    items_herrajes = []
    
    # Especificación de peso de vidrio OnVentanas
    items_herrajes.append({
        'icono': 'bi-speedometer2',
        'nombre': 'Peso del Vidrio (Fórmula OnVentanas)',
        'cantidad': f'{peso_total_vidrio_kg} kg',
        'detalle': f'{peso_hoja_vidrio_kg} kg/hoja ({area_total_m2:.2f} m² x {espesor_total_vidrio_mm} mm x 2.5)'
    })
    
    items_herrajes.append({
        'icono': 'bi-tools',
        'nombre': 'Tornillos Anclaje a Muro',
        'cantidad': tornillos_muro,
        'detalle': 'Pija #10 x 1½" con Taco Fisher nylon'
    })
    
    items_herrajes.append({
        'icono': 'bi-gear-wide-connected',
        'nombre': 'Tornillos Armado Aluminio',
        'cantidad': tornillos_armado,
        'detalle': 'Pija autoperforante #8 x ¾" cabeza fijadora'
    })
    
    if tipo_est == 'box_bano':
        items_herrajes.append({
            'icono': 'bi-shield-check',
            'nombre': 'Seguro / Cierre Magnético',
            'cantidad': 1,
            'detalle': 'Perfil con burlete magnético hermético'
        })
        items_herrajes.append({
            'icono': 'bi-circle',
            'nombre': 'Tirador / Manilla Inox',
            'cantidad': max(1, num_moviles),
            'detalle': 'Tirador toallero acero inoxidable con tornillo pasante'
        })
        items_herrajes.append({
            'icono': 'bi-arrow-left-right',
            'nombre': 'Carretillas / Roldanas',
            'cantidad': max(1, num_moviles) * 2,
            'detalle': 'Roldanas colgantes de acero inoxidable con rulemán'
        })
    elif apertura == 'corrediza':
        nombre_seguro = 'Cerradura Pico de Loro con Llave' if tipo_est == 'puerta' else 'Seguro Embutido Caracol Lateral'
        items_herrajes.append({
            'icono': 'bi-lock-fill',
            'nombre': 'Seguro / Cerradura',
            'cantidad': max(1, num_moviles),
            'detalle': f'{nombre_seguro} con seguro interior'
        })
        
        # Selección de carretillas según peso por hoja de vidrio
        if peso_hoja_vidrio_kg > 40:
            detalle_carretilla = f'Garruchas tándem reforzadas doble rodamiento (soporta hasta {int(peso_hoja_vidrio_kg*1.5)} kg)'
        else:
            detalle_carretilla = 'Garruchas con rueda de nylon y rulemán blindado'
            
        items_herrajes.append({
            'icono': 'bi-arrow-left-right',
            'nombre': 'Carretillas / Rodamientos',
            'cantidad': max(1, num_moviles) * 2,
            'detalle': detalle_carretilla
        })
        items_herrajes.append({
            'icono': 'bi-shield-slash',
            'nombre': 'Guías y Topes Antirruido',
            'cantidad': max(1, num_moviles) * 2,
            'detalle': 'Topes de goma y patines guía de nylon'
        })
    elif apertura == 'batiente':
        num_bisagras = (3 if alto >= 180 else 2) * max(1, num_moviles)
        items_herrajes.append({
            'icono': 'bi-door-closed',
            'nombre': 'Bisagras de Aluminio',
            'cantidad': num_bisagras,
            'detalle': f'Bisagras reforzadas ({num_bisagras * 4} tornillos fijación)'
        })
        items_herrajes.append({
            'icono': 'bi-key',
            'nombre': 'Cerradura con Manija y Pestillo',
            'cantidad': max(1, num_moviles),
            'detalle': 'Chapa manija con cilindro de seguridad'
        })
    else:
        items_herrajes.append({
            'icono': 'bi-pin-angle',
            'nombre': 'Calzos de Acristalamiento',
            'cantidad': num_hojas * 4,
            'detalle': 'Calzos de asentamiento de neopreno'
        })

    metros_felpa = round(((ancho + alto) * 2 * num_hojas) / 100.0, 1)
    items_herrajes.append({
        'icono': 'bi-water',
        'nombre': 'Felpa Hermética Cortaviento',
        'cantidad': f'{metros_felpa} m',
        'detalle': 'Felpa siliconada perimetral de estanqueidad'
    })

    total_tornillos = tornillos_muro + tornillos_armado + (max(1, num_moviles) * 4)

    return {
        'analisis_estructural': {
            'estado': estado,
            'color': color_estado,
            'titulo': titulo_estado,
            'advertencia': advertencia,
            'espesor_recomendado_mm': espesor_min_sugerido,
            'flecha_estimada_mm': flecha_aprox_mm,
            'flecha_admisible_mm': flecha_admisible_mm,
            'viento_max_kmh': viento_max_kmh,
            'area_total_m2': round(area_total_m2, 2),
            'area_hoja_m2': round(area_hoja_m2, 2),
            'peso_total_vidrio_kg': peso_total_vidrio_kg,
            'peso_hoja_vidrio_kg': peso_hoja_vidrio_kg,
            'propiedades_vidrio': propiedades_vidrio
        },
        'despiece_herrajes': {
            'total_tornillos': total_tornillos,
            'tornillos_muro': tornillos_muro,
            'tornillos_armado': tornillos_armado,
            'pasos_w': pasos_w,
            'pasos_h': pasos_h,
            'items': items_herrajes
        }
    }


def calcular_despiece_perfiles(datos):
    ancho = float(datos.get('ancho_cm', 120))
    alto = float(datos.get('alto_cm', 190))
    serie = datos.get('serie_aluminio', 'serie_30')
    perfil_tipo = datos.get('perfil_tipo', 'gancho')
    apertura = datos.get('apertura', 'corrediza')
    num_hojas = int(datos.get('numero_hojas', 2)) or 1
    tipo_est = datos.get('tipo_estructura', 'ventana')
    marco = datos.get('marco', 'normal')
    
    cortes = []
    
    # Metadata técnica de series de aluminio (pesos, tolerancias y descuentos estándar de taller)
    meta_serie = {
        'serie_20': {'nombre': 'Serie 20 (Económica)', 'peso_kg_m': 0.55, 'espesor_pared_mm': 1.1, 'dimension_seccion': '45x32 mm (pared 1.1 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 3.5, 'descuento_marco': 3.0, 'solape': 2.5},
        'serie_25': {'nombre': 'Serie 25 (Residencial)', 'peso_kg_m': 0.70, 'espesor_pared_mm': 1.2, 'dimension_seccion': '50x36 mm (pared 1.2 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 4.0, 'descuento_marco': 3.5, 'solape': 2.5},
        'serie_30': {'nombre': 'Serie 30 (Estándar Tradicional)', 'peso_kg_m': 0.95, 'espesor_pared_mm': 1.4, 'dimension_seccion': '60x42 mm (pared 1.4 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 4.5, 'descuento_marco': 4.0, 'solape': 3.0},
        'serie_35': {'nombre': 'Serie 35 (Comercial)', 'peso_kg_m': 1.15, 'espesor_pared_mm': 1.6, 'dimension_seccion': '70x46 mm (pared 1.6 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 5.0, 'descuento_marco': 4.5, 'solape': 3.0},
        'serie_40': {'nombre': 'Serie 40 (Puertas Reforzadas)', 'peso_kg_m': 1.45, 'espesor_pared_mm': 1.8, 'dimension_seccion': '80x55 mm (pared 1.8 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 6.0, 'descuento_marco': 5.5, 'solape': 4.0},
        'serie_60': {'nombre': 'Serie 60/Módena (Alta Gama RPT)', 'peso_kg_m': 1.85, 'espesor_pared_mm': 2.2, 'dimension_seccion': '90x62 mm (pared 2.2 mm RPT)', 'corte_angulo': '45° inglete', 'descuento_parante': 6.5, 'descuento_marco': 6.0, 'solape': 4.0},
        'serie_80': {'nombre': 'Serie 80 (Muro Cortina/Fachadas)', 'peso_kg_m': 2.60, 'espesor_pared_mm': 2.8, 'dimension_seccion': '100x70 mm (pared 2.8 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 7.0, 'descuento_marco': 7.0, 'solape': 5.0},
        'tubo_2x1': {'nombre': 'Tubo Rectangular 2"x1" (50x25 mm)', 'peso_kg_m': 0.65, 'espesor_pared_mm': 1.2, 'dimension_seccion': '50x25 mm (pared 1.2 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 5.0, 'descuento_marco': 5.0, 'solape': 0},
        'tubo_1x1': {'nombre': 'Tubo Cuadrado 1"x1" (25x25 mm)', 'peso_kg_m': 0.42, 'espesor_pared_mm': 1.2, 'dimension_seccion': '25x25 mm (pared 1.2 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 2.5, 'descuento_marco': 2.5, 'solape': 0},
        'tubo_3x1_5': {'nombre': 'Tubo Rectangular 3"x1½" (76x38 mm)', 'peso_kg_m': 1.10, 'espesor_pared_mm': 1.5, 'dimension_seccion': '76x38 mm (pared 1.5 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 7.6, 'descuento_marco': 7.6, 'solape': 0},
        'perfil_u': {'nombre': 'Canal Perfil U 1/2" (Templado)', 'peso_kg_m': 0.30, 'espesor_pared_mm': 1.5, 'dimension_seccion': '15x15 mm (pared 1.5 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 2.0, 'descuento_marco': 2.0, 'solape': 0},
        'serie_box': {'nombre': 'Línea Box de Baño', 'peso_kg_m': 0.85, 'espesor_pared_mm': 1.3, 'dimension_seccion': '40x25 mm (pared 1.3 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 3.0, 'descuento_marco': 3.0, 'solape': 3.0},
    }.get(serie, {'nombre': 'Serie 30 (Estándar Tradicional)', 'peso_kg_m': 0.95, 'espesor_pared_mm': 1.4, 'dimension_seccion': '60x42 mm (pared 1.4 mm)', 'corte_angulo': '90° recto', 'descuento_parante': 4.5, 'descuento_marco': 4.0, 'solape': 3.0})
    
    forma = datos.get('forma', 'lineal')
    profundidad = float(datos.get('profundidad_cm', 0))
    is_sin_marco = marco == 'ninguno'
    
    if tipo_est == 'box_bano' or is_sin_marco:
        if forma == 'esquinero' and profundidad > 0:
            cortes.append({
                'perfil': 'Riel Superior Guía Box Lado A',
                'codigo': 'BX-01A',
                'cantidad': 1,
                'longitud_cm': ancho,
                'corte': '45° inglete unión',
                'formula': 'Ancho Lado A'
            })
            cortes.append({
                'perfil': 'Riel Superior Guía Box Lado B',
                'codigo': 'BX-01B',
                'cantidad': 1,
                'longitud_cm': profundidad,
                'corte': '45° inglete unión',
                'formula': 'Profundidad Lado B'
            })
            cortes.append({
                'perfil': 'Guía Inferior Estanca Lado A',
                'codigo': 'BX-02A',
                'cantidad': 1,
                'longitud_cm': ancho,
                'corte': '45° inglete',
                'formula': 'Ancho Lado A'
            })
            cortes.append({
                'perfil': 'Guía Inferior Estanca Lado B',
                'codigo': 'BX-02B',
                'cantidad': 1,
                'longitud_cm': profundidad,
                'corte': '45° inglete',
                'formula': 'Profundidad Lado B'
            })
        else:
            cortes.append({
                'perfil': 'Riel Superior Guía Box Inox/Alu',
                'codigo': 'BX-01',
                'cantidad': 1,
                'longitud_cm': ancho,
                'corte': '90° recto',
                'formula': 'Ancho total luz'
            })
            cortes.append({
                'perfil': 'Guía / Zócalo Inferior Estanco',
                'codigo': 'BX-02',
                'cantidad': 1,
                'longitud_cm': ancho,
                'corte': '90° recto',
                'formula': 'Ancho total luz'
            })
        cortes.append({
            'perfil': 'Perfil U Fijación Lateral a Pared',
            'codigo': 'PU-20',
            'cantidad': 2,
            'longitud_cm': alto,
            'corte': '90° recto',
            'formula': 'Alto total luz'
        })
        if num_hojas > 1:
            cortes.append({
                'perfil': 'Perfil Portaburlete / Cierre Magnético',
                'codigo': 'BX-05',
                'cantidad': 1,
                'longitud_cm': round(alto - 4.0, 1),
                'corte': '90° recto',
                'formula': 'Alto - 4 cm'
            })
    elif serie.startswith('tubo'):
        cortes.append({
            'perfil': 'Tubo Dintel Superior',
            'codigo': 'TB-SUP',
            'cantidad': 1,
            'longitud_cm': ancho,
            'corte': '90° recto',
            'formula': 'Ancho total'
        })
        cortes.append({
            'perfil': 'Tubo Umbral Inferior',
            'codigo': 'TB-INF',
            'cantidad': 1,
            'longitud_cm': ancho,
            'corte': '90° recto',
            'formula': 'Ancho total'
        })
        h_jamba = round(alto - meta_serie['descuento_marco'], 1)
        cortes.append({
            'perfil': 'Tubo Jambas Laterales',
            'codigo': 'TB-JAM',
            'cantidad': 2,
            'longitud_cm': h_jamba,
            'corte': '90° recto',
            'formula': f"Alto - {meta_serie['descuento_marco']} cm"
        })
        cortes.append({
            'perfil': 'Pisavidrio / Junquillo Horizontales',
            'codigo': 'JQ-HOR',
            'cantidad': 2,
            'longitud_cm': round(ancho - meta_serie['descuento_marco']*2, 1),
            'corte': '45° inglete',
            'formula': 'Luz interior marco'
        })
        cortes.append({
            'perfil': 'Pisavidrio / Junquillo Verticales',
            'codigo': 'JQ-VER',
            'cantidad': 2,
            'longitud_cm': round(alto - meta_serie['descuento_marco']*2, 1),
            'corte': '45° inglete',
            'formula': 'Luz interior marco'
        })
    else:
        es_inglete = meta_serie['corte_angulo'] == '45° inglete'
        
        # 1. Marco Exterior
        cortes.append({
            'perfil': 'Riel Superior (Cabezal Marco)',
            'codigo': 'MK-RS',
            'cantidad': 1,
            'longitud_cm': ancho,
            'corte': '45° inglete' if es_inglete else '90° recto',
            'formula': 'Ancho total'
        })
        cortes.append({
            'perfil': 'Riel Inferior (Umbral con Guía Rodamiento)',
            'codigo': 'MK-RI',
            'cantidad': 1,
            'longitud_cm': ancho,
            'corte': '45° inglete' if es_inglete else '90° recto',
            'formula': 'Ancho total'
        })
        h_jamba = alto if es_inglete else round(alto - meta_serie['descuento_marco'], 1)
        cortes.append({
            'perfil': 'Jambas Laterales (Marco Vertical)',
            'codigo': 'MK-JB',
            'cantidad': 2,
            'longitud_cm': h_jamba,
            'corte': '45° inglete' if es_inglete else '90° recto',
            'formula': 'Alto total' if es_inglete else f"Alto - {meta_serie['descuento_marco']} cm"
        })
        
        # 2. Hojas Móviles / Fijas
        ancho_hoja = round((ancho + meta_serie['solape'] * (num_hojas - 1)) / num_hojas, 1)
        long_zocalo = round(ancho_hoja - meta_serie['descuento_parante'], 1)
        long_parante = round(alto - meta_serie['descuento_marco'], 1)
        
        cortes.append({
            'perfil': 'Zócalo Inferior de Hoja (Porta Garruchas)',
            'codigo': 'HJ-ZC',
            'cantidad': num_hojas,
            'longitud_cm': long_zocalo,
            'corte': '90° recto',
            'formula': f"Ancho hoja ({ancho_hoja}) - {meta_serie['descuento_parante']} cm"
        })
        cortes.append({
            'perfil': 'Cabezal Superior de Hoja',
            'codigo': 'HJ-CB',
            'cantidad': num_hojas,
            'longitud_cm': long_zocalo,
            'corte': '90° recto',
            'formula': f"Ancho hoja ({ancho_hoja}) - {meta_serie['descuento_parante']} cm"
        })
        
        # Parantes: Pierna Lateral (Cierre) y Pierna Gancho (Traslape central)
        if num_hojas == 1:
            cortes.append({
                'perfil': 'Piernas Laterales (Parantes Verticales)',
                'codigo': 'HJ-LT',
                'cantidad': 2,
                'longitud_cm': long_parante,
                'corte': '90° recto',
                'formula': f"Alto - {meta_serie['descuento_marco']} cm"
            })
        elif num_hojas == 2:
            cortes.append({
                'perfil': 'Piernas Laterales (Parantes de Cierre / Chapa)',
                'codigo': 'HJ-LT',
                'cantidad': 2,
                'longitud_cm': long_parante,
                'corte': '90° recto',
                'formula': f"Alto - {meta_serie['descuento_marco']} cm"
            })
            cortes.append({
                'perfil': 'Piernas Gancho / Traslape (Enclave Hermético Central)',
                'codigo': 'HJ-GC',
                'cantidad': 2,
                'longitud_cm': long_parante,
                'corte': '90° recto',
                'formula': f"Alto - {meta_serie['descuento_marco']} cm"
            })
        else: # 3 o 4 hojas
            num_ganchos = (num_hojas - 1) * 2
            num_laterales = 2
            cortes.append({
                'perfil': 'Piernas Laterales (Parantes de Cierre)',
                'codigo': 'HJ-LT',
                'cantidad': num_laterales,
                'longitud_cm': long_parante,
                'corte': '90° recto',
                'formula': f"Alto - {meta_serie['descuento_marco']} cm"
            })
            cortes.append({
                'perfil': 'Piernas Gancho / Traslape (Enclaves Centrales)',
                'codigo': 'HJ-GC',
                'cantidad': num_ganchos,
                'longitud_cm': long_parante,
                'corte': '90° recto',
                'formula': f"Alto - {meta_serie['descuento_marco']} cm"
            })
            
    # 3. OPTIMIZACIÓN DE BARRAS DE 6 METROS (Criterio Luminio / Taller de Carpintería de Aluminio)
    total_longitud_cm = 0.0
    total_piezas = 0
    for c in cortes:
        total_longitud_cm += c['longitud_cm'] * c['cantidad']
        total_piezas += c['cantidad']
        
    merma_disco_cm = total_piezas * 0.3
    longitud_con_disco_cm = total_longitud_cm + merma_disco_cm
    
    # Cada barra comercial estándar de 6.00 m tiene ~585 cm netos útiles restando despuntes
    barras_6m = max(1, math.ceil(longitud_con_disco_cm / 585.0))
    metros_lineales_utiles = round(total_longitud_cm / 100.0, 2)
    metros_totales_barras = barras_6m * 6.0
    merma_retazo_m = round(metros_totales_barras - metros_lineales_utiles, 2)
    porcentaje_aprovechamiento = round((metros_lineales_utiles / metros_totales_barras) * 100, 1)
    porcentaje_merma = round(100.0 - porcentaje_aprovechamiento, 1)
    
    peso_total_aluminio_kg = round(metros_lineales_utiles * meta_serie['peso_kg_m'], 2)
    
    return {
        'serie_nombre': meta_serie['nombre'],
        'espesor_pared_mm': meta_serie.get('espesor_pared_mm', 1.4),
        'dimension_seccion': meta_serie.get('dimension_seccion', ''),
        'peso_estimado_kg': peso_total_aluminio_kg,
        'peso_kg_m': meta_serie['peso_kg_m'],
        'barras_6m_requeridas': barras_6m,
        'metros_lineales_utiles': metros_lineales_utiles,
        'metros_totales_barras': metros_totales_barras,
        'merma_retazo_m': merma_retazo_m,
        'porcentaje_aprovechamiento': porcentaje_aprovechamiento,
        'porcentaje_merma': porcentaje_merma,
        'total_piezas': total_piezas,
        'cortes': cortes
    }
