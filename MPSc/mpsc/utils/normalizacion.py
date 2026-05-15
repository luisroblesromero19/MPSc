"""
MPSc — utils/normalizacion.py
Funciones de normalización: z-score, ajuste por liga, conversión a escala 1-10
"""


def convertir_por_90(total: float, minutos: float) -> float:
    if minutos <= 0:
        return 0.0
    return (total / minutos) * 90


def z_score(valor: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        return 0.0
    return (valor - mu) / sigma


def ajustar_por_liga(z: float, coeficiente: float) -> float:
    return z * coeficiente


def z_a_escala_10(z_ajustado: float) -> float:
    """
    Convierte z-score ajustado a escala 1-10.
    z = -3 → 1 | z = 0 → 5.5 | z = +3 → 10
    """
    z = max(-3.0, min(3.0, z_ajustado))
    return ((z + 3) / 6) * 9 + 1


def normalizar_metrica(valor: float, mu: float, sigma: float, coef_liga: float) -> float:
    z = z_score(valor, mu, sigma)
    z_adj = ajustar_por_liga(z, coef_liga)
    return round(z_a_escala_10(z_adj), 2)


def compatibilidad_modulo(score_a: float, score_b: float) -> float:
    return round(1 - (abs(score_a - score_b) / 10), 4)
