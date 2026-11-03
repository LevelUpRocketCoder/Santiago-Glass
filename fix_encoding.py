import os

files = [
    'templates/cotizaciones/lista.html',
    'templates/proyectos/tablero.html',
    'templates/cotizaciones/productos.html',
    'templates/clientes/lista.html',
    'templates/base.html',
    'templates/reportes/dashboard.html',
    'templates/cotizaciones/form.html',
    'cotizaciones/urls.py',
    'cotizaciones/models.py',
    'cotizaciones/views.py'
]

for fpath in files:
    if os.path.exists(fpath):
        # Read with ISO-8859-1 or whatever fallback, then rewrite as UTF-8
        try:
            with open(fpath, 'rb') as f:
                content = f.read()
            
            # Try to decode as utf-16 if it has null bytes (PowerShell might have done this)
            if b'\x00' in content:
                text = content.decode('utf-16le', errors='replace')
            else:
                # Try utf-8, fallback to latin1
                try:
                    text = content.decode('utf-8')
                except:
                    text = content.decode('latin1')
            
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error on {fpath}: {e}")

