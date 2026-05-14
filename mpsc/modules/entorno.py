"""
MPSc — modules/entorno.py
Módulo: Entorno competitivo (jugador y club)
"""
from config import COEFICIENTES_LIGA


class ModuloEntorno:

    def calcular(self, liga: str, posicion_tabla: int,
                 total_equipos: int, tiene_copa: bool,
                 tiene_internacional: bool) -> float:

        coef = COEFICIENTES_LIGA.get(liga, 0.70)
        score_liga = coef * 10

        # Percentil de posición en tabla
        if total_equipos > 1:
            percentil = 1 - ((posicion_tabla - 1) / (total_equipos - 1))
        else:
            percentil = 1.0

        if percentil >= 0.80:
            score_tabla = 9.0
        elif percentil >= 0.60:
            score_tabla = 7.0
        elif percentil >= 0.40:
            score_tabla = 6.0
        elif percentil >= 0.25:
            score_tabla = 4.5
        else:
            score_tabla = 2.0

        # Competencias activas
        if tiene_copa and tiene_internacional:
            score_comp = 10.0
        elif tiene_copa:
            score_comp = 7.0
        elif percentil >= 0.40:
            score_comp = 5.0
        else:
            score_comp = 3.0

        score = (score_liga * 0.50) + (score_tabla * 0.30) + (score_comp * 0.20)
        return round(score, 2)
