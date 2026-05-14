"""
MPSc — modules/viabilidad.py
Módulo: Viabilidad contractual
"""


class ModuloViabilidad:

    def score_contrato(self, meses: int) -> float:
        if meses <= 6:   return 10.0
        if meses <= 12:  return 8.0
        if meses <= 18:  return 6.0
        if meses <= 24:  return 4.0
        return 2.0

    def score_clausula(self, tiene_clausula: bool, nivel: str) -> float:
        if not tiene_clausula:
            return 10.0
        return 8.0 if nivel == "accesible" else 5.0

    def calcular(self, meses_contrato: int, tiene_clausula: bool,
                 clausula_nivel: str) -> float:
        s_contrato = self.score_contrato(meses_contrato)
        s_clausula = self.score_clausula(tiene_clausula, clausula_nivel)
        score = (s_contrato * 0.60) + (s_clausula * 0.40)
        return round(score, 2)
