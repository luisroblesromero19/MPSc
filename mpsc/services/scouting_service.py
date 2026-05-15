"""
MPSc — services/scouting_service.py
Motor de búsqueda masiva de jugadores compatibles.
Busca automáticamente jugadores cuyo perfil táctico encaje
con las necesidades detectadas de un club.
"""

from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy.orm import Session
from mpsc.database.connection import get_session
from mpsc.database.repositories.club_repository import ClubRepository
from mpsc.database.repositories.temporada_club_repository import TemporadaClubRepository
from mpsc.database.repositories.jugador_repository import JugadorRepository
from mpsc.database.repositories.temporada_repository import TemporadaRepository
from mpsc.database.adapters import orm_a_jugador
from mpsc.database.models.jugador_model import JugadorORM
from mpsc.database.models.club_model import ClubORM
from mpsc.modules.inferencia_tactica import inferir_perfil, PerfilTacticoClub
from mpsc.modules.detector_necesidades import DetectorNecesidades, NecesidadTactica
from mpsc.modules.vectorizacion import compatibilidad_tactica, generar_vector_jugador
from mpsc.models.jugador import Jugador


@dataclass
class ResultadoScouting:
    """Resultado de una búsqueda de scouting automático."""

    jugador: Jugador
    score_compatibilidad: float
    score_tactico: float
    score_contextual: float
    confianza_estadistica: float
    fortalezas_detectadas: List[str]
    riesgos_detectados: List[str]
    necesidades_cubiertas: List[str]

    def __repr__(self):
        return (
            f"ResultadoScouting(jugador='{self.jugador.nombre}', "
            f"score={self.score_compatibilidad:.2f})"
        )


class ScoutingService:

    def __init__(self, session: Optional[Session] = None):
        self._session_own = session is None
        self.session = session or get_session()
        self.club_repo = ClubRepository(self.session)
        self.temp_club_repo = TemporadaClubRepository(self.session)
        self.jug_repo = JugadorRepository(self.session)
        self.temp_repo = TemporadaRepository(self.session)
        self.detector = DetectorNecesidades()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_own:
            self.session.close()

    def buscar_jugadores_compatibles(
        self,
        club_id: int,
        perfil: str = "rendimiento_inmediato",
        limit: int = 20,
        filtros: Optional[dict] = None,
    ) -> List[ResultadoScouting]:
        """Busca los jugadores más compatibles para un club.

        Pipeline:
        1. Obtener club + última temporada
        2. Inferir perfil táctico del club
        3. Detectar necesidades
        4. Generar vector de necesidad
        5. Consultar jugadores históricos
        6. Para cada jugador: generar vector, calcular compatibilidad
        7. Ordenar y retornar top candidatos
        """
        club_orm = self.club_repo.obtener_por_id(club_id)
        if club_orm is None:
            return []

        temp_club = self.temp_club_repo.obtener_ultima_por_club(club_id)
        if temp_club is None:
            return []

        stats_club = {c.name: getattr(temp_club, c.name) for c in temp_club.__table__.columns}
        perfil_tactico = inferir_perfil(stats_club, temp_club.partidos)
        necesidades = self.detector.detectar(perfil_tactico)

        jugadores_orm = self.jug_repo.listar(limit=100)

        filtros = filtros or {}
        pos_filtro = filtros.get("posicion", "").lower().strip()

        resultados: List[ResultadoScouting] = []

        for jorm in jugadores_orm:
            ultima_temp = self.temp_repo.obtener_ultima_por_jugador(jorm.id)
            jugador = orm_a_jugador(jorm, ultima_temp)

            if pos_filtro and jugador.posicion.lower().strip() != pos_filtro:
                continue

            tactico = compatibilidad_tactica(jugador, perfil_tactico, necesidades)

            resultado = ResultadoScouting(
                jugador=jugador,
                score_compatibilidad=tactico["score_tactico"],
                score_tactico=tactico["score_tactico"],
                score_contextual=0.5,
                confianza_estadistica=tactico["confianza"],
                fortalezas_detectadas=tactico["fortalezas"],
                riesgos_detectados=tactico["riesgos"],
                necesidades_cubiertas=tactico["necesidades_cubiertas"],
            )
            resultados.append(resultado)

        resultados.sort(key=lambda r: r.score_compatibilidad, reverse=True)
        return resultados[:limit]
