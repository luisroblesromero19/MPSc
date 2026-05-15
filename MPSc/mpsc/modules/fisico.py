"""
MPSc — modules/fisico.py
Módulo: Físico y salud del jugador
"""


class ModuloFisico:

    TIPOS_LESION = {
        "ninguna":   (10, 10),
        "muscular":  (7,  6),
        "ligamento": (5,  4),
        "fractura":  (7,  7),
    }

    def score_historial(self, num_lesiones: int) -> float:
        if num_lesiones == 0:   return 10.0
        if num_lesiones == 1:   return 8.0
        if num_lesiones == 2:   return 6.0
        if num_lesiones == 3:   return 4.0
        return 2.0

    def score_tipo(self, tipo: str, semanas_baja: float) -> float:
        base_hist, base_grav = self.TIPOS_LESION.get(tipo, (6, 6))
        if semanas_baja <= 0:
            return 10.0
        if semanas_baja <= 3:
            penalizacion = 0
        elif semanas_baja <= 6:
            penalizacion = 1
        elif semanas_baja <= 12:
            penalizacion = 2
        else:
            penalizacion = 3
        return max(1.0, float(base_grav) - penalizacion)

    def score_carga(self, minutos_jugados: float, minutos_posibles: float) -> float:
        if minutos_posibles <= 0:
            return 5.0
        pct = (minutos_jugados / minutos_posibles) * 100
        if pct < 60:
            return 5.0
        if pct < 70:
            return round(5.0 + (pct - 60) * 0.5, 2)
        if pct <= 85:
            return 10.0
        if pct <= 92:
            return 8.0
        return 6.0

    def penalizacion_altitud(self, alt_origen: float, alt_destino: float) -> float:
        diff = abs(alt_destino - alt_origen)
        if diff < 500:    return 0.0
        if diff < 1500:   return 0.5
        if diff < 2500:   return 1.0
        return 2.0

    def calcular(self, num_lesiones: int, tipo_lesion: str,
                 semanas_baja: float, minutos_jugados: float,
                 minutos_posibles: float, altitud_origen: float,
                 altitud_destino: float) -> float:

        s_hist  = self.score_historial(num_lesiones)
        s_tipo  = self.score_tipo(tipo_lesion, semanas_baja)
        s_carga = self.score_carga(minutos_jugados, minutos_posibles)

        score_base = (s_hist * 0.50) + (s_tipo * 0.30) + (s_carga * 0.20)
        penal      = self.penalizacion_altitud(altitud_origen, altitud_destino)

        return round(max(1.0, score_base - penal), 2)
