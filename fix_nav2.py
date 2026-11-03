with open('templates/base.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

nav_old = '''        <div class="nav-links">
            <a href="{% url 'dashboard' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}">
                <i class="bi bi-grid-1x2"></i> Dashboard
            </a>
            <a href="{% url 'lista_clientes' %}" class="nav-link {% if 'cliente' in request.path %}active{% endif %}">
                <i class="bi bi-people"></i> Clientes
            </a>
            <a href="{% url 'lista_cotizaciones' %}" class="nav-link {% if 'cotizacion' in request.path %}active{% endif %}">
                <i class="bi bi-file-earmark-text"></i> Cotizaciones
            </a>
            <a href="{% url 'tablero' %}" class="nav-link {% if 'proyecto' in request.path %}active{% endif %}">
                <i class="bi bi-kanban"></i> Proyectos
            </a>
            <a href="{% url 'lista_productos' %}" class="nav-link {% if 'producto' in request.path %}active{% endif %}">
                <i class="bi bi-grid-3x3-gap"></i> Catálogo
            </a>
            <a href="{% url 'reporte' %}" class="nav-link {% if 'reporte' in request.path %}active{% endif %}">
                <i class="bi bi-bar-chart"></i> Reportes
            </a>
            <a href="{% url 'diseno_wizard' %}" class="nav-link {% if 'diseno' in request.path %}active{% endif %}" style="color:var(--gold); border: 1px solid var(--gold-glow); background: rgba(251,191,36,0.1);">
                <i class="bi bi-vector-pen"></i> Diseño
            </a>
        </div>'''

start_idx = content.find('<div class="nav-links">')
end_idx = content.find('</div>', start_idx) + 6

if start_idx != -1:
    new_content = content[:start_idx] + nav_old + content[end_idx:]
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
