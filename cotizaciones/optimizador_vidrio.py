"""
Optimizador de corte de planchas de vidrio 2D (Guillotine Cutting Stock Optimizer)
Diseñado para talleres de vidrio y aluminio - Santiago Glass
"""
from typing import List, Dict, Any
import math

class GlassPiece:
    def __init__(self, id_pieza: str, ancho: float, alto: float, rotar: bool = True, desc: str = ""):
        self.id_pieza = id_pieza
        self.ancho = float(ancho)
        self.alto = float(alto)
        self.rotar = rotar
        self.desc = desc or id_pieza
        self.colocada = False

class FreeRect:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def area(self):
        return self.w * self.h

class GlassSheet:
    def __init__(self, numero: int, ancho: float, alto: float):
        self.numero = numero
        self.ancho = float(ancho)
        self.alto = float(alto)
        self.piezas_colocadas: List[Dict[str, Any]] = []
        self.free_rects: List[FreeRect] = [FreeRect(0, 0, self.ancho, self.alto)]
        self.area_total = self.ancho * self.alto
        self.area_usada = 0.0

    @property
    def aprovechamiento(self) -> float:
        if self.area_total <= 0:
            return 0.0
        return round((self.area_usada / self.area_total) * 100, 1)

    @property
    def merma(self) -> float:
        return round(100.0 - self.aprovechamiento, 1)

def optimizar_planchas_vidrio(
    piezas_input: List[Dict[str, Any]],
    ancho_plancha: float = 3600.0,
    alto_plancha: float = 2400.0,
    margen_corte: float = 4.0,
    permitir_rotacion: bool = True
) -> Dict[str, Any]:
    """
    Algoritmo 2D Guillotine Cutting para planchas industriales de vidrio.
    """
    # 1. Expandir piezas con sus cantidades
    lista_piezas: List[GlassPiece] = []
    for idx, p in enumerate(piezas_input, 1):
        cant = int(p.get("cantidad", 1))
        ancho = float(p.get("ancho", 100))
        alto = float(p.get("alto", 100))
        label = p.get("label", f"P{idx}")
        desc = p.get("desc", f"{ancho:.0f}x{alto:.0f}")

        for c in range(cant):
            ref = f"{label} ({c+1})" if cant > 1 else label
            lista_piezas.append(GlassPiece(ref, ancho, alto, rotar=permitir_rotacion, desc=desc))

    # Ordenar piezas por área descendente (Best-Fit Decreasing)
    lista_piezas.sort(key=lambda item: max(item.ancho, item.alto) * min(item.ancho, item.alto), reverse=True)

    planchas: List[GlassSheet] = []

    for pieza in lista_piezas:
        colocada = False

        # Intentar colocar en planchas ya abiertas
        for sheet in planchas:
            if colocar_en_hoja(sheet, pieza, margen_corte):
                colocada = True
                break

        # Si no cupo en ninguna, abrir nueva plancha
        if not colocada:
            nueva_hoja = GlassSheet(len(planchas) + 1, ancho_plancha, alto_plancha)
            colocar_en_hoja(nueva_hoja, pieza, margen_corte)
            planchas.append(nueva_hoja)

    # Calcular estadísticas globales
    area_total_planchas_m2 = (len(planchas) * ancho_plancha * alto_plancha) / 1_000_000
    area_cortada_m2 = sum(p.ancho * p.alto for p in lista_piezas) / 1_000_000
    aprovechamiento_global = round((area_cortada_m2 / area_total_planchas_m2 * 100), 1) if area_total_planchas_m2 > 0 else 0.0
    merma_global = round(100.0 - aprovechamiento_global, 1)

    resultado = {
        "total_planchas": len(planchas),
        "total_piezas": len(lista_piezas),
        "ancho_plancha": ancho_plancha,
        "alto_plancha": alto_plancha,
        "area_total_m2": round(area_total_planchas_m2, 2),
        "area_cortada_m2": round(area_cortada_m2, 2),
        "aprovechamiento_global": aprovechamiento_global,
        "merma_global": merma_global,
        "planchas": []
    }

    palette_colors = [
        "#38BDF8", "#F59E0B", "#10B981", "#818CF8", "#F472B6", 
        "#34D399", "#FBBF24", "#60A5FA", "#A78BFA", "#4ADE80"
    ]

    for sheet in planchas:
        # Extraer retazos útiles (más de 150x150 mm)
        retazos_utiles = [
            {"x": r.x, "y": r.y, "w": r.w, "h": r.h, "area_m2": round((r.w * r.h) / 1_000_000, 3)}
            for r in sheet.free_rects if r.w >= 150 and r.h >= 150
        ]
        # Asignar colores agradables a las piezas
        piezas_coloreadas = []
        for idx_p, p_col in enumerate(sheet.piezas_colocadas):
            p_copy = dict(p_col)
            p_copy["color"] = palette_colors[idx_p % len(palette_colors)]
            piezas_coloreadas.append(p_copy)

        resultado["planchas"].append({
            "numero": sheet.numero,
            "ancho": sheet.ancho,
            "alto": sheet.alto,
            "aprovechamiento": sheet.aprovechamiento,
            "merma": sheet.merma,
            "piezas": piezas_coloreadas,
            "retazos": retazos_utiles,
            "num_piezas": len(sheet.piezas_colocadas)
        })

    return resultado


def colocar_en_hoja(sheet: GlassSheet, pieza: GlassPiece, margen: float) -> bool:
    """
    Encuentra el mejor espacio libre en la hoja usando Guillotine Cutting.
    """
    best_idx = -1
    best_rotated = False
    min_residual_area = float('inf')

    w = pieza.ancho
    h = pieza.alto

    for idx, r in enumerate(sheet.free_rects):
        # Probar orientación normal
        if w + margen <= r.w and h + margen <= r.h:
            residual = (r.w * r.h) - (w * h)
            if residual < min_residual_area:
                min_residual_area = residual
                best_idx = idx
                best_rotated = False

        # Probar orientación rotada 90° si está permitido
        if pieza.rotar and (h + margen <= r.w and w + margen <= r.h):
            residual = (r.w * r.h) - (h * w)
            if residual < min_residual_area:
                min_residual_area = residual
                best_idx = idx
                best_rotated = True

    if best_idx == -1:
        return False

    free_rect = sheet.free_rects.pop(best_idx)
    pw = h if best_rotated else w
    ph = w if best_rotated else h

    # Registrar pieza colocada
    sheet.piezas_colocadas.append({
        "id": pieza.id_pieza,
        "x": round(free_rect.x, 1),
        "y": round(free_rect.y, 1),
        "w": round(pw, 1),
        "h": round(ph, 1),
        "rotada": best_rotated,
        "desc": pieza.desc,
        "ancho_original": pieza.ancho,
        "alto_original": pieza.alto
    })

    sheet.area_usada += (pw * ph)

    # División de corte guillotina (Split)
    # Crea 2 nuevos rectángulos libres a la derecha y abajo
    ancho_ocupado = pw + margen
    alto_ocupado = ph + margen

    # Opción 1: corte vertical
    rect_derecha = FreeRect(free_rect.x + ancho_ocupado, free_rect.y, free_rect.w - ancho_ocupado, alto_ocupado)
    rect_abajo = FreeRect(free_rect.x, free_rect.y + alto_ocupado, free_rect.w, free_rect.h - alto_ocupado)

    if rect_derecha.w > 10 and rect_derecha.h > 10:
        sheet.free_rects.append(rect_derecha)
    if rect_abajo.w > 10 and rect_abajo.h > 10:
        sheet.free_rects.append(rect_abajo)

    # Ordenar rectángulos libres por tamaño para optimizar futuros encajes
    sheet.free_rects.sort(key=lambda r: r.area)

    return True
