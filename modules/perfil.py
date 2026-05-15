"""
MPSc — modules/perfil.py
Módulo: Perfil base del jugador
"""


class ModuloPerfil:

    ROLES = {
        "titular_indiscutible": 10,
        "titular_con_competencia": 8,
        "rotacion_habitual": 6,
        "suplente": 4,
        "sin_minutos": 1,
    }

    def score_edad(self, edad: int) -> float:
        if 17 <= edad <= 19: return 5.0
        if 20 <= edad <= 23: return 8.0
        if 24 <= edad <= 27: return 10.0
        if 28 <= edad <= 30: return 7.0
        return 4.0

    def score_minutos(self, minutos_jugados: float, minutos_posibles: float) -> float:
        if minutos_posibles <= 0:
            return 1.0
        pct = (minutos_jugados / minutos_posibles) * 100
        if pct >= 90:   return 10.0
        if pct >= 75:   return 8.0
        if pct >= 60:   return 6.0
        if pct >= 45:   return 4.0
        return 2.0

    def calcular(self, edad: int, rol: str,
                 minutos_jugados: float, minutos_posibles: float,
                 filtro_duro_ok: bool = True) -> float:

        s_edad     = self.score_edad(edad)
        s_rol      = float(self.ROLES.get(rol, 5))
        s_minutos  = self.score_minutos(minutos_jugados, minutos_posibles)

        score = (s_edad * 0.25) + (s_rol * 0.35) + (s_minutos * 0.40)

        if not filtro_duro_ok:
            score = min(score, 3.0)

        return round(score, 2)
