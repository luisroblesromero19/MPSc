"""
MPSc — services/temporada_service.py
Servicio de negocio para gestión de temporadas históricas.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from mpsc.database.connection import get_session
from mpsc.database.repositories.temporada_repository import TemporadaRepository
from mpsc.database.adapters import jugador_a_temporada
from mpsc.models.jugador import Jugador
from mpsc.database.models.temporada_model import TemporadaORM


class TemporadaService:

    def __init__(self, session: Optional[Session] = None):
        self._session_own = session is None
        self.session = session or get_session()
        self.repo = TemporadaRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_own:
            self.session.close()

    def agregar_temporada(self, jugador_id: int, jugador: Jugador, temporada: str = "") -> TemporadaORM:
        temp_orm = jugador_a_temporada(jugador, temporada)
        temp_orm.jugador_id = jugador_id
        self.session.add(temp_orm)
        self.session.commit()
        self.session.refresh(temp_orm)
        return temp_orm

    def obtener_historico(self, jugador_id: int) -> List[TemporadaORM]:
        return self.repo.obtener_por_jugador(jugador_id)

    def obtener_ultima_temporada(self, jugador_id: int) -> Optional[TemporadaORM]:
        return self.repo.obtener_ultima_por_jugador(jugador_id)

    def eliminar_temporada(self, temporada_id: int) -> bool:
        return self.repo.eliminar(temporada_id)
