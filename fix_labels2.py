import re
with open('cotizaciones/dibujo_ventana.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"{color_alum.capitalize()} color aluminum frame"', 'f"Marco de aluminio {color_alum.capitalize()}"')
text = text.replace('"5mm+9A+5mm double clear glass"', '"Vidrio doble claro"')
text = text.replace('"Clear float glass"', '"Vidrio simple"')
text = text.replace('"Two channels frame"', '"Marco de 2 canales (Corrediza)"')
text = text.replace('"Fixed frame"', '"Marco fijo (Entera)"')
text = text.replace('"Grill design inside glass"', '"Diseño de rejilla interno"')

with open('cotizaciones/dibujo_ventana.py', 'w', encoding='utf-8') as f:
    f.write(text)
