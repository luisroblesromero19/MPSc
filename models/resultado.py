"""
MPSc — models/resultado.py
Clase Resultado: encapsula el índice de compatibilidad final.
"""
from dataclasses import dataclass, field


TABLA_INTERPRETACION = {
    1: [
        (85, "MUY ALTA — Candidato prioritario"),
        (70, "ALTA — Candidato recomendado"),
        (55, "MODERADA — Candidato con reservas"),
        (40, "BAJA — Brechas importantes"),
        (0,  "MUY BAJA — No recomendado"),
    ],
    2: [
        (85, "MUY ALTA — Candidato recomendado con monitoreo"),
        (70, "ALTA — Candidato con reservas"),
        (55, "MODERADA — Alto riesgo"),
        (40, "BAJA — No recomendado"),
        (0,  "MUY BAJA — No recomendado"),
    ],
    3: [
        (85, "MUY ALTA — Candidato con reservas serias"),
        (70, "ALTA — Alto riesgo"),
        (55, "MODERADA — No recomendado"),
        (40, "BAJA — No recomendado"),
        (0,  "MUY BAJA — No recomendado"),
    ],
}


@dataclass
class Resultado:
    nombre_jugador: str = ""
    nombre_club: str = ""
    valor_mercado: str = ""
    perfil_evaluacion: str = ""

    compatibilidades: dict = field(default_factory=dict)
    scores_jugador: dict = field(default_factory=dict)
    scores_club: dict = field(default_factory=dict)

    nivel_brecha: int = 1
    delta_coef: float = 0.0
    penalizacion_aplicada: float = 0.0

    factor_contexto_global: float = 1.0
    confiabilidad_estadisticas: float = 1.0

    score_rendimiento_inmediato: float = 0.0
    score_potencial_mediano: float = 0.0
    score_bajo_riesgo: float = 0.0
    score_final: float = 0.0

    def interpretacion(self) -> str:
        tabla = TABLA_INTERPRETACION.get(self.nivel_brecha, TABLA_INTERPRETACION[1])
        s = self.score_final
        for umbral, texto in tabla:
            if s >= umbral:
                return texto
        return "MUY BAJA — No recomendado"

    def color_interpretacion(self) -> str:
        s = self.score_final
        if s >= 85:   return "#22c55e"
        elif s >= 70: return "#84cc16"
        elif s >= 55: return "#f59e0b"
        elif s >= 40: return "#f97316"
        else:         return "#ef4444"
