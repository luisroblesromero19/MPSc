"""
MPSc — modules/detector_necesidades.py
Detección automática de necesidades tácticas del club.
Convierte un PerfilTacticoClub en una lista de necesidades
estructuradas con rol, prioridad y motivo.

Sistema extensible basado en reglas heurísticas.
"""

from dataclasses import dataclass, field
from typing import List
from .inferencia_tactica import PerfilTacticoClub


@dataclass
class NecesidadTactica:
    """Una necesidad táctica detectada en el club."""

    rol: str
    prioridad: float
    motivo: str
    metricas_relacionadas: List[str] = field(default_factory=list)

    def __repr__(self):
        return (
            f"NecesidadTactica(rol='{self.rol}', "
            f"prioridad={self.prioridad:.2f}, "
            f"motivo='{self.motivo}')"
        )


class DetectorNecesidades:
    """Detector de necesidades basado en reglas heurísticas.

    Cada regla examina el perfil táctico y produce una NecesidadTactica
    con prioridad proporcional a la desviación del valor ideal (5.0).
    """

    def __init__(self, umbral_activacion: float = 2.5):
        self.umbral = umbral_activacion

    def detectar(self, perfil: PerfilTacticoClub) -> List[NecesidadTactica]:
        necesidades: List[NecesidadTactica] = []

        for regla in self._reglas():
            necesidad = regla(perfil)
            if necesidad is not None:
                necesidades.append(necesidad)

        necesidades.sort(key=lambda n: n.prioridad, reverse=True)
        return necesidades

    def _reglas(self):
        return [
            self._regla_delantero_finalizador,
            self._regla_mediocampista_creativo,
            self._regla_central_dominante,
            self._regla_extremo_ofensivo,
            self._regla_mediocentro_defensivo,
            self._regla_lateral_ofensivo,
            self._regla_mediocampista_boxes,
        ]

    # ── Reglas individuales ──────────────────────────────────────

    def _regla_delantero_finalizador(self, p: PerfilTacticoClub):
        """Volumen alto + eficiencia baja → necesitan finalizador."""
        if p.volumen_ofensivo >= 6.0 and p.eficiencia_ofensiva <= 4.5:
            desviacion = (p.volumen_ofensivo - p.eficiencia_ofensiva) / 10.0
            return NecesidadTactica(
                rol="delantero_centro",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Baja eficiencia ofensiva con alto volumen de tiros",
                metricas_relacionadas=["eficiencia_ofensiva", "volumen_ofensivo"],
            )
        return None

    def _regla_mediocampista_creativo(self, p: PerfilTacticoClub):
        """Posesión alta + progresión baja → necesitan creador."""
        if p.posesion >= 6.5 and p.progresion <= 5.0:
            desviacion = (p.posesion - p.progresion) / 10.0
            return NecesidadTactica(
                rol="mediocampista_central",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Posesión alta pero progresión baja",
                metricas_relacionadas=["posesion", "progresion"],
            )
        return None

    def _regla_central_dominante(self, p: PerfilTacticoClub):
        """Fragilidad aérea alta → necesitan central dominante."""
        if p.fragilidad_aerea >= 6.5:
            prioridad = round(min((p.fragilidad_aerea - 5.0) / 5.0, 1.0), 4)
            return NecesidadTactica(
                rol="central",
                prioridad=prioridad,
                motivo="Alta fragilidad defensiva aérea",
                metricas_relacionadas=["fragilidad_aerea"],
            )
        return None

    def _regla_extremo_ofensivo(self, p: PerfilTacticoClub):
        """Amplitud baja + dependencia de bandas baja → falta desborde."""
        if p.amplitud <= 4.0 and p.dependencia_bandas <= 4.0:
            desviacion = (5.0 - p.amplitud) / 5.0
            return NecesidadTactica(
                rol="extremo",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Baja amplitud ofensiva, falta desborde por bandas",
                metricas_relacionadas=["amplitud", "dependencia_bandas"],
            )
        return None

    def _regla_lateral_ofensivo(self, p: PerfilTacticoClub):
        """Amplitud baja + centros bajos → necesitan lateral ofensivo."""
        if p.amplitud <= 4.5 and p.metricas_fuente.get("centros_pp", 5) <= 6.0:
            desviacion = (5.0 - p.amplitud) / 5.0
            return NecesidadTactica(
                rol="lateral",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Poca profundidad por laterales, pocos centros",
                metricas_relacionadas=["amplitud"],
            )
        return None

    def _regla_mediocentro_defensivo(self, p: PerfilTacticoClub):
        """Intensidad de presión baja → necesitan mediocentro defensivo."""
        if p.intensidad_presion <= 4.5:
            desviacion = (5.0 - p.intensidad_presion) / 5.0
            return NecesidadTactica(
                rol="mediocampista_defensivo",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Baja intensidad de presión en el medio",
                metricas_relacionadas=["intensidad_presion"],
            )
        return None

    def _regla_mediocampista_boxes(self, p: PerfilTacticoClub):
        """Fragilidad defensiva alta + volumen ofensivo medio → box-to-box."""
        if p.fragilidad_defensiva >= 6.0 and 4.0 <= p.volumen_ofensivo <= 7.0:
            desviacion = (p.fragilidad_defensiva - 5.0) / 5.0
            return NecesidadTactica(
                rol="mediocampista_central",
                prioridad=round(min(desviacion, 1.0), 4),
                motivo="Desequilibrio entre fragilidad defensiva y volumen ofensivo",
                metricas_relacionadas=["fragilidad_defensiva", "volumen_ofensivo"],
            )
        return None
