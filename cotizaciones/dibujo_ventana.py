def generar_svg(ancho, alto, tipo='ventana', estilo='corrediza', rejilla=True, color_alum='blanco', vidrio='doble'):
    svg_width = 800
    svg_height = 650
    margen_x = 180
    margen_y = 100
    
    ancho_dibujo = svg_width - (margen_x * 2)
    alto_dibujo = svg_height - (margen_y * 2)
    
    if ancho <= 0 or alto <= 0: return "<svg></svg>"

    escala_x = ancho_dibujo / float(ancho)
    escala_y = alto_dibujo / float(alto)
    escala = min(escala_x, escala_y)
    
    w = float(ancho) * escala
    h = float(alto) * escala
    x = (svg_width - w) / 2
    y = (svg_height - h) / 2
    
    if tipo == 'puerta':
        y = svg_height - margen_y - h + 40
        
    # Paleta Foto-realista
    alum_colors = {
        'blanco': ('#ffffff', '#f8fafc', '#e2e8f0', '#cbd5e1'),
        'negro': ('#475569', '#334155', '#1e293b', '#0f172a'),
        'bronce': ('#b45309', '#92400e', '#78350f', '#451a03'),
        'natural': ('#f1f5f9', '#e2e8f0', '#cbd5e1', '#94a3b8')
    }
    c_highlight, c_face, c_shadow, c_deep = alum_colors.get(color_alum, alum_colors['blanco'])
    
    svg = f"<svg width='100%' height='100%' viewBox='0 0 {svg_width} {svg_height}' xmlns='http://www.w3.org/2000/svg'>\n"
    svg += f"""
    <defs>
        <!-- Marco Extrusión 3D (Corte) -->
        <linearGradient id="frameGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{c_highlight}"/>
            <stop offset="30%" stop-color="{c_face}"/>
            <stop offset="80%" stop-color="{c_shadow}"/>
            <stop offset="100%" stop-color="{c_deep}"/>
        </linearGradient>
        <linearGradient id="frameInner" x1="100%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="{c_highlight}"/>
            <stop offset="100%" stop-color="{c_shadow}"/>
        </linearGradient>
        
        <!-- Vidrio Realista con Reflejo de Entorno Simulado -->
        <linearGradient id="glassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#e0f2fe" stop-opacity="0.9"/>
            <stop offset="45%" stop-color="#bae6fd" stop-opacity="0.6"/>
            <stop offset="50%" stop-color="#ffffff" stop-opacity="0.9"/> <!-- Brillo diagonal -->
            <stop offset="55%" stop-color="#bae6fd" stop-opacity="0.5"/>
            <stop offset="100%" stop-color="#7dd3fc" stop-opacity="0.7"/>
        </linearGradient>
        
        <!-- Sombra paralela muy suave y realista -->
        <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="15" dy="25" stdDeviation="15" flood-color="#000000" flood-opacity="0.5"/>
        </filter>
        <filter id="innerShadow">
            <feDropShadow dx="3" dy="5" stdDeviation="5" flood-color="#000000" flood-opacity="0.6"/>
        </filter>
    </defs>
    
    <!-- Fondo decorativo tipo pared -->
    <rect width="100%" height="100%" fill="#1e1e1e" />
    <rect x="{x-40}" y="{y-40 if tipo=='ventana' else y}" width="{w+80}" height="{h+80 if tipo=='ventana' else h}" fill="#2d2d2d" rx="10"/>
    """
    
    g_marco = 28 # Marco muy grueso realista
    g_hoja = 24
    
    if tipo == 'puerta':
        piso_y = y + h
        svg += f"  <line x1='{x-100}' y1='{piso_y+5}' x2='{x+w+100}' y2='{piso_y+5}' stroke='#111' stroke-width='10'/>\n"
        svg += f"  <line x1='{x-100}' y1='{piso_y}' x2='{x+w+100}' y2='{piso_y}' stroke='#555' stroke-width='4'/>\n"
        # Riel inf
        svg += f"  <rect x='{x}' y='{piso_y-12}' width='{w}' height='12' fill='url(#frameGrad)'/>\n"
        # U invertida
        path_m = f"M {x},{piso_y-12} L {x},{y} L {x+w},{y} L {x+w},{piso_y-12} L {x+w-g_marco},{piso_y-12} L {x+w-g_marco},{y+g_marco} L {x+g_marco},{y+g_marco} L {x+g_marco},{piso_y-12} Z"
        svg += f"  <path d='{path_m}' fill='url(#frameGrad)' filter='url(#dropShadow)'/>\n"
        
        # Efecto de bisel en el marco interior
        path_bisel = f"M {x},{y} L {x+w},{y} L {x+w-g_marco},{y+g_marco} L {x+g_marco},{y+g_marco} Z"
        svg += f"  <path d='{path_bisel}' fill='{c_highlight}' opacity='0.4'/>\n"
        
        ix, iy, iw, ih = x + g_marco, y + g_marco, w - g_marco*2, h - g_marco - 12
    else:
        # Ventana 4 lados
        svg += f"  <rect x='{x}' y='{y}' width='{w}' height='{h}' fill='url(#frameGrad)' rx='4' filter='url(#dropShadow)'/>\n"
        # Bisel superior
        svg += f"  <polygon points='{x},{y} {x+w},{y} {x+w-g_marco},{y+g_marco} {x+g_marco},{y+g_marco}' fill='{c_highlight}' opacity='0.5'/>\n"
        # Bisel izquierdo
        svg += f"  <polygon points='{x},{y} {x+g_marco},{y+g_marco} {x+g_marco},{y+h-g_marco} {x},{y+h}' fill='{c_highlight}' opacity='0.2'/>\n"
        # Hueco negro de sombra (riel)
        ix, iy, iw, ih = x + g_marco, y + g_marco, w - g_marco*2, h - g_marco*2
        svg += f"  <rect x='{ix}' y='{iy}' width='{iw}' height='{ih}' fill='#111' filter='url(#innerShadow)'/>\n"

    paneles = []
    
    if estilo == 'corrediza':
        hoja_w = (iw / 2) + (g_hoja/2)
        
        # HOJA TRASERA (IZQUIERDA)
        hx1, hy1, hw1, hh1 = ix, iy, hoja_w, ih
        svg += f"  <rect x='{hx1}' y='{hy1}' width='{hw1}' height='{hh1}' fill='url(#frameInner)' stroke='#000' stroke-width='1'/>\n"
        # Goma negra + Vidrio
        gx1, gy1, gw1, gh1 = hx1 + g_hoja, hy1 + g_hoja, hw1 - g_hoja*2, hh1 - g_hoja*2
        svg += f"  <rect x='{gx1-3}' y='{gy1-3}' width='{gw1+6}' height='{gh1+6}' fill='#111827'/>\n" # Goma
        svg += f"  <rect x='{gx1}' y='{gy1}' width='{gw1}' height='{gh1}' fill='url(#glassGrad)'/>\n"
        paneles.append({'x': gx1, 'y': gy1, 'w': gw1, 'h': gh1})
        
        # HOJA DELANTERA (DERECHA)
        hx2, hy2, hw2, hh2 = ix + iw - hoja_w, iy, hoja_w, ih
        svg += f"  <rect x='{hx2}' y='{hy2}' width='{hw2}' height='{hh2}' fill='url(#frameGrad)' filter='url(#dropShadow)' stroke='#000' stroke-width='1'/>\n"
        # Goma negra + Vidrio
        gx2, gy2, gw2, gh2 = hx2 + g_hoja, hy2 + g_hoja, hw2 - g_hoja*2, hh2 - g_hoja*2
        svg += f"  <rect x='{gx2-3}' y='{gy2-3}' width='{gw2+6}' height='{gh2+6}' fill='#111827'/>\n" # Goma
        svg += f"  <rect x='{gx2}' y='{gy2}' width='{gw2}' height='{gh2}' fill='url(#glassGrad)'/>\n"
        paneles.append({'x': gx2, 'y': gy2, 'w': gw2, 'h': gh2})
        
        # Detalles de Aluminio (Manijas embutidas)
        if tipo == 'puerta':
            mh = ih * 0.3
            svg += f"  <rect x='{hx2+g_hoja+15}' y='{hy2+(ih-mh)/2}' width='12' height='{mh}' fill='#111' rx='4'/>\n"
            svg += f"  <rect x='{hx2+g_hoja+17}' y='{hy2+(ih-mh)/2+10}' width='8' height='{mh-20}' fill='#222' rx='2'/>\n"
        else:
            svg += f"  <rect x='{hx2+8}' y='{hy2+ih/2-40}' width='10' height='80' fill='#222' rx='4' filter='url(#innerShadow)'/>\n"
            svg += f"  <rect x='{hx1+hw1-18}' y='{hy1+ih/2-40}' width='10' height='80' fill='#222' rx='4' filter='url(#innerShadow)'/>\n"
    else:
        # FIJA (ENTERA)
        svg += f"  <rect x='{ix}' y='{iy}' width='{iw}' height='{ih}' fill='url(#frameInner)'/>\n"
        gx, gy, gw, gh = ix + g_hoja, iy + g_hoja, iw - g_hoja*2, ih - g_hoja*2
        svg += f"  <rect x='{gx-3}' y='{gy-3}' width='{gw+6}' height='{gh+6}' fill='#111827'/>\n"
        svg += f"  <rect x='{gx}' y='{gy}' width='{gw}' height='{gh}' fill='url(#glassGrad)'/>\n"
        paneles.append({'x': gx, 'y': gy, 'w': gw, 'h': gh})
        if tipo == 'puerta':
            mh = ih * 0.25
            svg += f"  <rect x='{gx+gw-40}' y='{gy+(gh-mh)/2}' width='15' height='{mh}' fill='#111' rx='6' filter='url(#dropShadow)'/>\n"

    # REJILLA INTERIOR REALISTA
    if rejilla:
        for p in paneles:
            vx, vy, vw, vh = p['x'], p['y'], p['w'], p['h']
            gw_grid = 10
            # Sombra de rejilla sobre el vidrio
            svg += f"  <rect x='{vx}' y='{vy + vh/3 - gw_grid/2}' width='{vw}' height='{gw_grid}' fill='#ffffff' filter='url(#innerShadow)' opacity='0.9'/>\n"
            svg += f"  <rect x='{vx}' y='{vy + (vh/3)*2 - gw_grid/2}' width='{vw}' height='{gw_grid}' fill='#ffffff' filter='url(#innerShadow)' opacity='0.9'/>\n"
            svg += f"  <rect x='{vx + vw/2 - gw_grid/2}' y='{vy}' width='{gw_grid}' height='{vh}' fill='#ffffff' filter='url(#innerShadow)' opacity='0.9'/>\n"

    # ETIQUETAS "IA" SOBRE EL RENDER OSCURO
    c_lbl = "#fbbf24"
    
    def dib_etiq(cx, cy, ex, ey, txt, align="right"):
        out = f"  <circle cx='{cx}' cy='{cy}' r='5' fill='{c_lbl}' filter='url(#dropShadow)'/>\n"
        mid_x = cx + (ex - cx)/2
        out += f"  <polyline points='{cx},{cy} {mid_x},{ey} {ex},{ey}' fill='none' stroke='{c_lbl}' stroke-width='2' filter='url(#dropShadow)'/>\n"
        anch = "start" if align=="right" else "end"
        tx = ex + 10 if align=="right" else ex - 10
        out += f"  <text x='{tx}' y='{ey+5}' text-anchor='{anch}' fill='#ffffff' font-size='15' font-weight='700' font-family='sans-serif' filter='url(#dropShadow)'>{txt}</text>\n"
        return out

    svg += dib_etiq(x + w/2, y + g_marco/2, x + w/2 + 150, y - 50, f"Marco Aluminio {color_alum.capitalize()}", "right")
    
    vid_x = x + w/4
    vid_y = y + h - 80
    txt_vid = "Vidrio Doble (5mm+9A+5mm)" if vidrio == 'doble' else "Vidrio Simple"
    svg += dib_etiq(vid_x, vid_y, x - 30, vid_y + 50, txt_vid, "left")
    
    tipo_l = "Marco Doble Canal" if estilo=='corrediza' else "Marco Simple Fijo"
    svg += dib_etiq(x + w - 40, y + h - 40, x + w + 110, y + h + 20, tipo_l, "right")
    
    if rejilla:
        svg += dib_etiq(x + w/4 + 10, y + h/3, x - 50, y + h/3 - 40, "Diseño Rejilla Interior", "left")

    svg += "</svg>"
    return svg
