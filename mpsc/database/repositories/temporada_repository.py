"""
MPSc — database/repositories/temporada_repository.py
CRUD para temporadas históricas del jugador.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.temporada_model import TemporadaORM


class TemporadaRepository:

    def __init__(self, session: Session):
        self.session = session

    def crear(self, datos: dict) -> TemporadaORM:
        temporada = TemporadaORM(**datos)
        self.session.add(temporada)
        self.session.commit()
        self.session.refresh(temporada)
        return temporada

    def obtener_por_id(self, temporada_id: int) -> Optional[TemporadaORM]:
        return self.session.query(TemporadaORM).filter(TemporadaORM.id == temporada_id).first()

    def obtener_por_jugador(self, jugador_id: int) -> List[TemporadaORM]:
        return (
            self.session.query(TemporadaORM)
            .filter(TemporadaORM.jugador_id == jugador_id)
            .order_by(TemporadaORM.temporada.desc())
            .all()
        )

    def obtener_ultima_por_jugador(self, jugador_id: int) -> Optional[TemporadaORM]:
        return (
            self.session.query(TemporadaORM)
            .filter(TemporadaORM.jugador_id == jugador_id)
            .order_by(TemporadaORM.temporada.desc())
            .first()
        )

    def eliminar(self, temporada_id: int) -> bool:
        temporada = self.obtener_por_id(temporada_id)
        if temporada is None:
            return False
        self.session.delete(temporada)
        self.session.commit()
        return True
