"""
MPSc — database/repositories/temporada_club_repository.py
CRUD para temporadas estadísticas del club.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.temporada_club_model import TemporadaClubORM


class TemporadaClubRepository:

    def __init__(self, session: Session):
        self.session = session

    def crear(self, datos: dict) -> TemporadaClubORM:
        temp = TemporadaClubORM(**datos)
        self.session.add(temp)
        self.session.commit()
        self.session.refresh(temp)
        return temp

    def obtener_por_id(self, temp_id: int) -> Optional[TemporadaClubORM]:
        return self.session.query(TemporadaClubORM).filter(TemporadaClubORM.id == temp_id).first()

    def obtener_por_club(self, club_id: int) -> List[TemporadaClubORM]:
        return (
            self.session.query(TemporadaClubORM)
            .filter(TemporadaClubORM.club_id == club_id)
            .order_by(TemporadaClubORM.temporada.desc())
            .all()
        )

    def obtener_ultima_por_club(self, club_id: int) -> Optional[TemporadaClubORM]:
        return (
            self.session.query(TemporadaClubORM)
            .filter(TemporadaClubORM.club_id == club_id)
            .order_by(TemporadaClubORM.temporada.desc())
            .first()
        )

    def eliminar(self, temp_id: int) -> bool:
        temp = self.obtener_por_id(temp_id)
        if temp is None:
            return False
        self.session.delete(temp)
        self.session.commit()
        return True
