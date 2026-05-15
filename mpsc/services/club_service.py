"""
MPSc — services/club_service.py
Servicio de negocio para gestión de clubes.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from mpsc.database.connection import get_session
from mpsc.database.repositories.club_repository import ClubRepository
from mpsc.database.repositories.temporada_club_repository import TemporadaClubRepository
from mpsc.database.models.club_model import ClubORM
from mpsc.database.models.temporada_club_model import TemporadaClubORM


class ClubService:

    def __init__(self, session: Optional[Session] = None):
        self._session_own = session is None
        self.session = session or get_session()
        self.club_repo = ClubRepository(self.session)
        self.temp_repo = TemporadaClubRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_own:
            self.session.close()

    def crear_club(self, datos_base: dict) -> ClubORM:
        return self.club_repo.crear(datos_base)

    def obtener_club(self, club_id: int) -> Optional[ClubORM]:
        return self.club_repo.obtener_por_id(club_id)

    def listar_clubes(self, offset: int = 0, limit: int = 100) -> List[ClubORM]:
        return self.club_repo.listar(offset, limit)

    def actualizar_club(self, club_id: int, datos: dict) -> Optional[ClubORM]:
        return self.club_repo.actualizar(club_id, datos)

    def eliminar_club(self, club_id: int) -> bool:
        return self.club_repo.eliminar(club_id)

    def buscar_por_nombre(self, nombre: str) -> List[ClubORM]:
        return self.club_repo.buscar_por_nombre(nombre)

    def agregar_temporada(
        self, club_id: int, datos_stats: dict
    ) -> TemporadaClubORM:
        datos_stats["club_id"] = club_id
        return self.temp_repo.crear(datos_stats)

    def obtener_temporadas(self, club_id: int) -> List[TemporadaClubORM]:
        return self.temp_repo.obtener_por_club(club_id)

    def obtener_ultima_temporada(self, club_id: int) -> Optional[TemporadaClubORM]:
        return self.temp_repo.obtener_ultima_por_club(club_id)
