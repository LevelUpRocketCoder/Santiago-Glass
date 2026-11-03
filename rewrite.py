import os

files_to_write = {
    'templates/cotizaciones/productos.html': '''{% extends 'base.html' %}
{% block title %}Catálogo | Santiago Glass{% endblock %}
{% block page_title %}Catálogo de Productos{% endblock %}
{% block content %}
<div class="card fade-in">
    <div class="card-header">
        <span><i class="bi bi-grid-3x3-gap" style="color:var(--gold); margin-right:8px;"></i> Catálogo</span>
        <a href="{% url 'nuevo_producto' %}" class="btn btn-red btn-sm"><i class="bi bi-plus-lg"></i> Nuevo Producto</a>
    </div>
    <div class="card-body-0 table-wrap">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Unidad</th>
                    <th>Precio ()</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {% for p in productos %}
                <tr>
                    <td style="font-weight:bold; color:var(--text);">{{ p.nombre }}</td>
                    <td style="color:var(--text-dim);">{{ p.descripcion|truncatechars:50 }}</td>
                    <td>{{ p.get_unidad_medida_display }}</td>
                    <td style="font-weight:bold; color:var(--gold);"> {{ p.precio_unitario }}</td>
                    <td><span class="badge badge-{% if p.activo %}aprobada{% else %}rechazada{% endif %}">{% if p.activo %}Activo{% else %}Inactivo{% endif %}</span></td>
                </tr>
                {% empty %}
                <tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-dim);">No hay productos en el catálogo.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''',

    'templates/cotizaciones/lista.html': '''{% extends 'base.html' %}
{% block title %}Cotizaciones | Santiago Glass{% endblock %}
{% block page_title %}Cotizaciones{% endblock %}
{% block content %}
<div class="card fade-in">
    <div class="card-header">
        <span><i class="bi bi-file-earmark-text" style="color:var(--red); margin-right:8px;"></i> Todas las Cotizaciones</span>
        <a href="{% url 'nueva_cotizacion' %}" class="btn btn-red btn-sm"><i class="bi bi-plus-lg"></i> Nueva Cotización</a>
    </div>
    <div class="card-body-0 table-wrap">
        <table class="data-table">
            <thead>
                <tr>
                    <th>N°</th>
                    <th>Cliente</th>
                    <th>Fecha</th>
                    <th>Total ()</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for c in cotizaciones %}
                <tr>
                    <td style="font-weight:bold; color:var(--text);">{{ c.numero }}</td>
                    <td>{{ c.cliente.nombre_completo }}</td>
                    <td style="color:var(--text-dim);">{{ c.fecha|date:"d M Y" }}</td>
                    <td style="font-weight:bold; color:var(--gold);"> {{ c.total }}</td>
                    <td><span class="badge badge-{{ c.estado }}">{{ c.get_estado_display }}</span></td>
                    <td>
                        <a href="{% url 'detalle_cotizacion' c.pk %}" class="btn btn-ghost btn-sm">Ver Detalles</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--text-dim);">No hay cotizaciones registradas.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''',

    'templates/proyectos/tablero.html': '''{% extends 'base.html' %}
{% block title %}Proyectos | Santiago Glass{% endblock %}
{% block page_title %}Tablero de Proyectos{% endblock %}
{% block content %}
<div class="card fade-in">
    <div class="card-header">
        <span><i class="bi bi-kanban" style="color:var(--blue); margin-right:8px;"></i> Tablero de Proyectos</span>
    </div>
    <div class="card-body-0 table-wrap">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Proyecto (Cotización)</th>
                    <th>Cliente</th>
                    <th>Inicio Estimado</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for p in proyectos %}
                <tr>
                    <td style="font-weight:bold; color:var(--text);">{{ p.cotizacion.numero }}</td>
                    <td>{{ p.cotizacion.cliente.nombre_completo }}</td>
                    <td style="color:var(--text-dim);">{{ p.fecha_inicio_estimada|date:"d M Y"|default:"-" }}</td>
                    <td><span class="badge badge-{{ p.estado|slugify }}">{{ p.get_estado_display }}</span></td>
                    <td>
                        <a href="{% url 'detalle_proyecto' p.pk %}" class="btn btn-ghost btn-sm">Ver Proyecto</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-dim);">No hay proyectos registrados.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''',

    'templates/clientes/lista.html': '''{% extends 'base.html' %}
{% block title %}Clientes | Santiago Glass{% endblock %}
{% block page_title %}Clientes Registrados{% endblock %}
{% block content %}
<div class="card fade-in">
    <div class="card-header">
        <span><i class="bi bi-people" style="color:var(--green); margin-right:8px;"></i> Todos los Clientes</span>
        <a href="{% url 'nuevo_cliente' %}" class="btn btn-red btn-sm"><i class="bi bi-person-plus"></i> Nuevo Cliente</a>
    </div>
    <div class="card-body-0 table-wrap">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Nombre Completo</th>
                    <th>Documento / NIT</th>
                    <th>Celular</th>
                    <th>Email</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for c in clientes %}
                <tr>
                    <td style="font-weight:bold; color:var(--text);">{{ c.nombre_completo }}</td>
                    <td>{{ c.documento_identidad|default:"-" }}</td>
                    <td>{{ c.celular|default:"-" }}</td>
                    <td style="color:var(--text-dim);">{{ c.email|default:"-" }}</td>
                    <td>
                        <a href="{% url 'detalle_cliente' c.pk %}" class="btn btn-ghost btn-sm">Ver / Editar</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-dim);">No hay clientes registrados.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''
}

for fpath, text in files_to_write.items():
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)

