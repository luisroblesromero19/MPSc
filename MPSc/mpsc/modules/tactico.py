"""
MPSc — modules/tactico.py
Módulos interpretativos: modelo de juego y proyecto deportivo
"""


class ModuloModeloJuego:
    """
    Scores ingresados manualmente por el scout (1-10 por fase).
    El cálculo es el promedio de las tres fases.
    """

    def calcular(self, score_ofensiva: float,
                 score_defensiva: float,
                 score_transicion: float) -> float:
        score = (score_ofensiva + score_defensiva + score_transicion) / 3
        return round(score, 2)


class ModuloProyecto:
    """
    Scores ingresados manualmente por el scout (1-10 cada criterio).
    """

    def calcular(self, alineacion_edad: float,
                 alineacion_perfil: float,
                 continuidad: float) -> float:
        score = (alineacion_edad + alineacion_perfil + continuidad) / 3
        return round(score, 2)


class ModuloActualidadClub:
    """
    Calcula el score de actualidad deportiva del club
    a partir de datos brutos: posición, forma reciente y competencias.
    """

    def score_forma(self, victorias: int, empates: int, derrotas: int) -> float:
        puntos = (victorias * 3) + (empates * 1)
        max_pts = (victorias + empates + derrotas) * 3
        if max_pts == 0:
            return 5.0
        return round(((puntos / max_pts) * 9) + 1, 2)

    def score_posicion(self, posicion: int, total_equipos: int) -> float:
        if total_equipos <= 1:
            return 5.0
        percentil = 1 - ((posicion - 1) / (total_equipos - 1))
        if percentil >= 0.80: return 9.0
        if percentil >= 0.60: return 7.0
        if percentil >= 0.40: return 6.0
        if percentil >= 0.25: return 4.5
        return 2.0

    def score_competencias(self, tiene_copa: bool, tiene_internacional: bool) -> float:
        if tiene_copa and tiene_internacional: return 10.0
        if tiene_copa:                         return 7.0
        return 5.0

    def calcular(self, posicion: int, total_equipos: int,
                 victorias: int, empates: int, derrotas: int,
                 tiene_copa: bool, tiene_internacional: bool) -> float:
        s_pos   = self.score_posicion(posicion, total_equipos)
        s_forma = self.score_forma(victorias, empates, derrotas)
        s_comp  = self.score_competencias(tiene_copa, tiene_internacional)
        score   = (s_pos * 0.50) + (s_forma * 0.30) + (s_comp * 0.20)
        return round(score, 2)
