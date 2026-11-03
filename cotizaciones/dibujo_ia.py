def generar_svg_ia(params):
    ancho = params['ancho_cm']
    alto = params['alto_cm']
    tipo = params['tipo_estructura']
    hojas_list = params['hojas']
    numero_hojas = len(hojas_list)
    rejilla = params['rejilla']
    color_alum = params['color_aluminio']
    vidrio = params['tipo_vidrio']
    apertura = params['apertura']

    svg_width = 1000
    svg_height = 800
    # Ajuste de encuadre (Punto 6) - mas espacio para evitar solapamiento
    margen_x = 250
    margen_y = 150
    
    ancho_dibujo = svg_width - (margen_x * 2)
    alto_dibujo = svg_height - (margen_y * 2)
    
    if ancho <= 0 or alto <= 0: return "<svg></svg>"

    escala = min(ancho_dibujo / float(ancho), alto_dibujo / float(alto))
    w = float(ancho) * escala
    h = float(alto) * escala
    x = (svg_width - w) / 2
    y = (svg_height - h) / 2
    
    if tipo == 'puerta' or tipo == 'box_bano': 
        y = svg_height - margen_y - h + 60
        
    alum_colors = {
        'blanco': ('#ffffff', '#f8fafc', '#e2e8f0', '#cbd5e1'),
        'negro': ('#475569', '#334155', '#1e293b', '#0f172a'),
        'bronce': ('#b45309', '#92400e', '#78350f', '#451a03'),
        'natural': ('#f1f5f9', '#e2e8f0', '#cbd5e1', '#94a3b8'),
        'mate': ('#f8fafc', '#e2e8f0', '#cbd5e1', '#94a3b8'),
        'brillante': ('#ffffff', '#ffffff', '#e2e8f0', '#94a3b8'),
        'champagne': ('#fde68a', '#d97706', '#b45309', '#78350f'),
        'titanio': ('#94a3b8', '#64748b', '#475569', '#334155'),
        'madera': ('#78350f', '#451a03', '#451a03', '#1a0d00')
    }
    c_highlight, c_face, c_shadow, c_deep = alum_colors.get(color_alum, alum_colors['blanco'])
    
    svg = f"<svg width='100%' height='100%' viewBox='0 0 {svg_width} {svg_height}' xmlns='http://www.w3.org/2000/svg'>\n"
    svg += f'''<defs>
        <linearGradient id="frameGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{c_highlight}"/><stop offset="30%" stop-color="{c_face}"/><stop offset="80%" stop-color="{c_shadow}"/><stop offset="100%" stop-color="{c_deep}"/>
        </linearGradient>
        <linearGradient id="frameInner" x1="100%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="{c_highlight}"/><stop offset="100%" stop-color="{c_shadow}"/>
        </linearGradient>
        <linearGradient id="glassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#e0f2fe" stop-opacity="0.9"/>
            <stop offset="45%" stop-color="#bae6fd" stop-opacity="0.6"/>
            <stop offset="50%" stop-color="#ffffff" stop-opacity="0.9"/>
            <stop offset="55%" stop-color="#bae6fd" stop-opacity="0.5"/>
            <stop offset="100%" stop-color="#7dd3fc" stop-opacity="0.7"/>
        </linearGradient>
        <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="15" dy="25" stdDeviation="15" flood-color="#000000" flood-opacity="0.5"/></filter>
        <filter id="innerShadow"><feDropShadow dx="3" dy="5" stdDeviation="5" flood-color="#000000" flood-opacity="0.6"/></filter>
    </defs>'''
    
    g_marco = 25
    g_hoja = 22
    
    if tipo == 'box_bano':
        g_marco = 10
        g_hoja = 10
        # Box de baño: Riel superior grueso, no marco lateral ni inferior grueso
        svg += f"  <rect x='{x}' y='{y}' width='{w}' height='15' fill='url(#frameGrad)' filter='url(#dropShadow)'/>\n"
        ix, iy, iw, ih = x, y + 15, w, h - 15
    elif tipo == 'puerta':
        piso_y = y + h
        svg += f"  <line x1='{x-100}' y1='{piso_y+5}' x2='{x+w+100}' y2='{piso_y+5}' stroke='#111' stroke-width='10'/>\n"
        svg += f"  <rect x='{x}' y='{piso_y-12}' width='{w}' height='12' fill='url(#frameGrad)'/>\n"
        path_m = f"M {x},{piso_y-12} L {x},{y} L {x+w},{y} L {x+w},{piso_y-12} L {x+w-g_marco},{piso_y-12} L {x+w-g_marco},{y+g_marco} L {x+g_marco},{y+g_marco} L {x+g_marco},{piso_y-12} Z"
        svg += f"  <path d='{path_m}' fill='url(#frameGrad)' filter='url(#dropShadow)'/>\n"
        ix, iy, iw, ih = x + g_marco, y + g_marco, w - g_marco*2, h - g_marco - 12
    else:
        svg += f"  <rect x='{x}' y='{y}' width='{w}' height='{h}' fill='url(#frameGrad)' rx='4' filter='url(#dropShadow)'/>\n"
        ix, iy, iw, ih = x + g_marco, y + g_marco, w - g_marco*2, h - g_marco*2
        svg += f"  <rect x='{ix}' y='{iy}' width='{iw}' height='{ih}' fill='#111' filter='url(#innerShadow)'/>\n"

    hoja_w = (iw / numero_hojas) + (g_hoja/numero_hojas) if numero_hojas > 1 else iw
    
    for i, hoja in enumerate(hojas_list):
        hx = ix + i*(iw/numero_hojas) - (g_hoja/2 if i>0 and numero_hojas>1 else 0)
        
        is_movil = (hoja['tipo'] == 'movil')
        # Las moviles van al frente (shadow), fijas atras
        fill_marco = "url(#frameGrad)" if is_movil else "url(#frameInner)"
        filt = "filter='url(#dropShadow)'" if is_movil else ""
        
        # Marco de la hoja
        if tipo == 'box_bano':
            # Vidrio crudo sin marco grueso
            svg += f"  <rect x='{hx}' y='{iy}' width='{hoja_w}' height='{ih}' fill='url(#glassGrad)' {filt}/>\n"
            # Rodamiento superior si es movil
            if is_movil:
                svg += f"  <circle cx='{hx+20}' cy='{iy-7}' r='6' fill='#111'/>\n"
                svg += f"  <circle cx='{hx+hoja_w-20}' cy='{iy-7}' r='6' fill='#111'/>\n"
        else:
            svg += f"  <rect x='{hx}' y='{iy}' width='{hoja_w}' height='{ih}' fill='{fill_marco}' {filt} stroke='#000' stroke-width='1'/>\n"
            gx, gy, gw, gh = hx + g_hoja, iy + g_hoja, hoja_w - g_hoja*2, ih - g_hoja*2
            svg += f"  <rect x='{gx-3}' y='{gy-3}' width='{gw+6}' height='{gh+6}' fill='#111827'/>\n"
            svg += f"  <rect x='{gx}' y='{gy}' width='{gw}' height='{gh}' fill='url(#glassGrad)'/>\n"

        # Tiradores solo si es movil (Punto 4)
        if is_movil:
            mh = ih * 0.25
            # Poner manija a la derecha o izquierda dependiendo si es primera o ultima hoja
            mx = hx + 15 if i==0 and numero_hojas>1 else hx + hoja_w - 25
            if tipo == 'box_bano':
                mx = hx + hoja_w - 35
                svg += f"  <circle cx='{mx+5}' cy='{iy+ih/2}' r='15' fill='url(#frameGrad)' filter='url(#dropShadow)'/>\n"
            elif tipo == 'puerta':
                svg += f"  <rect x='{mx}' y='{iy+(ih-mh)/2}' width='12' height='{mh}' fill='#111' rx='4'/>\n"
            else:
                svg += f"  <rect x='{mx}' y='{iy+ih/2-40}' width='10' height='80' fill='#222' rx='4' filter='url(#innerShadow)'/>\n"

    # Cotas
    c_cota = "#fbbf24"
    svg += f"  <line x1='{x}' y1='{y-30}' x2='{x+w}' y2='{y-30}' stroke='{c_cota}' stroke-width='2'/>\n"
    svg += f"  <text x='{x+w/2}' y='{y-40}' text-anchor='middle' fill='{c_cota}' font-size='20' font-family='sans-serif' font-weight='bold'>↔ {ancho} cm</text>\n"
    
    svg += f"  <line x1='{x-40}' y1='{y}' x2='{x-40}' y2='{y+h}' stroke='{c_cota}' stroke-width='2'/>\n"
    svg += f"  <text x='{x-50}' y='{y+h/2}' text-anchor='middle' fill='{c_cota}' font-size='20' font-family='sans-serif' font-weight='bold' transform='rotate(-90 {x-50} {y+h/2})'>↕ {alto} cm</text>\n"

    svg += "</svg>"
    return svg
