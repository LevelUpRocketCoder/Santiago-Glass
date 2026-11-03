# Santiago Glass - Sistema Web de Cotizaciones y Gestión

Sistema de gestión comercial y técnica para carpintería de aluminio y vidrio. Permite registrar clientes, crear cotizaciones con renderizado visual e inteligencia artificial, exportar a Word y PDF, y dar seguimiento a los proyectos mediante un tablero Kanban.

## Características Principales

- **Dashboard:** Métricas comerciales, facturación semestral y actividad reciente.
- **Clientes:** Gestión integral de clientes y su historial de cotizaciones.
- **Cotizaciones:**
  - Cálculo automático de importes en Bolivianos y conversión de números a letras.
  - Diseñador visual con simulación de ventanas y puertas en SVG (vidrio simple/doble, perfiles, colores).
  - Diseñador asistido por IA mediante lenguaje natural (análisis de prompt y cotas).
  - Exportación profesional en formato Word (`.docx`) y PDF.
- **Proyectos (Kanban):** Flujo de trabajo por estados (*Cotizado*, *Aprobado*, *En Instalación*, *Entregado*) con registro cronológico de cambios.
- **Reportes:** Filtrado analítico por rango de fechas y estado de cotizaciones.
- **Suite de Pruebas Automatizadas:** 113 pruebas unitarias e integración con Django Test Runner.

## Requisitos y Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/LevelUpRocketCoder/Santiago-Glass.git
   cd Santiago-Glass
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```

5. Iniciar servidor:
   ```bash
   python manage.py runserver
   ```
   O en Windows hacer doble clic en `INICIAR.bat` o `launcher.vbs`.

## Ejecución de Pruebas

```bash
python manage.py test
```
