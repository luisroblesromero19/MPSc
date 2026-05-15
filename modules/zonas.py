"""
MPSc — modules/zonas.py
Módulo: Zonas de presencia — similitud coseno
"""
import math


class ModuloZonas:

    PESOS_RANKING = [5, 4, 3, 2, 1]
    NUM_ZONAS = 18

    def _construir_vector(self, zonas: list) -> list:
        vec = [0] * self.NUM_ZONAS
        for i, zona in enumerate(zonas[:5]):
            if 1 <= zona <= self.NUM_ZONAS:
                vec[zona - 1] += self.PESOS_RANKING[i]
        return vec

    def similitud_coseno(self, vec_a: list, vec_b: list) -> float:
        producto = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
        mag_b = math.sqrt(sum(b ** 2 for b in vec_b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return producto / (mag_a * mag_b)

    def calcular(self, zonas_jugador: list, zonas_club: list) -> float:
        vec_j = self._construir_vector(zonas_jugador)
        vec_c = self._construir_vector(zonas_club)
        sim   = self.similitud_coseno(vec_j, vec_c)
        score = sim * 9 + 1
        return round(score, 2)
