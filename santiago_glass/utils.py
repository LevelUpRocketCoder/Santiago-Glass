def numero_a_letras(numero):
    """Convierte un número a su representación en letras (español) para uso en cotizaciones."""
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
    especiales = {11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE',
                  16: 'DIECISEIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE',
                  21: 'VEINTIUN', 22: 'VEINTIDOS', 23: 'VEINTITRES', 24: 'VEINTICUATRO',
                  25: 'VEINTICINCO', 26: 'VEINTISEIS', 27: 'VEINTISIETE', 28: 'VEINTIOCHO', 29: 'VEINTINUEVE'}
    centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS',
                'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']

    def _convertir_grupo(n):
        if n == 0: return ''
        if n == 100: return 'CIEN'
        resultado = ''
        c = n // 100
        r = n % 100
        if c > 0: resultado = centenas[c] + ' '
        if r in especiales: resultado += especiales[r]
        elif r > 0:
            d = r // 10
            u = r % 10
            if d > 0 and u > 0:
                resultado += decenas[d] + ' Y ' + unidades[u]
            elif d > 0:
                resultado += decenas[d]
            else:
                resultado += unidades[u]
        return resultado.strip()

    try:
        numero = float(numero)
    except (ValueError, TypeError):
        return 'CERO 00/100'

    entero = int(numero)
    decimales = int(round((numero - entero) * 100))

    if entero == 0:
        return f'CERO {decimales:02d}/100'

    partes = []
    if entero >= 1000000:
        millones = entero // 1000000
        entero %= 1000000
        if millones == 1: partes.append('UN MILLON')
        else: partes.append(_convertir_grupo(millones) + ' MILLONES')
    if entero >= 1000:
        miles = entero // 1000
        entero %= 1000
        if miles == 1: partes.append('MIL')
        else: partes.append(_convertir_grupo(miles) + ' MIL')
    if entero > 0:
        partes.append(_convertir_grupo(entero))

    texto = ' '.join(partes)
    return f'{texto} {decimales:02d}/100'
