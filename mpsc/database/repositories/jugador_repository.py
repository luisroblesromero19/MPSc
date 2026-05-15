"""
MPSc — database/repositories/jugador_repository.py
CRUD completo para la entidad JugadorORM.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.jugador_model import JugadorORM


class JugadorRepository:

    def __init__(self, session: Session):
        self.session = session

    def crear(self, datos: dict) -> JugadorORM:
        jugador = JugadorORM(**datos)
        self.session.add(jugador)
        self.session.commit()
        self.session.refresh(jugador)
        return jugador

    def obtener_por_id(self, jugador_id: int) -> Optional[JugadorORM]:
        return self.session.query(JugadorORM).filter(JugadorORM.id == jugador_id).first()

    def listar(self, offset: int = 0, limit: int = 100) -> List[JugadorORM]:
        return (
            self.session.query(JugadorORM)
            .order_by(JugadorORM.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def actualizar(self, jugador_id: int, datos: dict) -> Optional[JugadorORM]:
        jugador = self.obtener_por_id(jugador_id)
        if jugador is None:
            return None
        for clave, valor in datos.items():
            if hasattr(jugador, clave):
                setattr(jugador, clave, valor)
        self.session.commit()
        self.session.refresh(jugador)
        return jugador

    def eliminar(self, jugador_id: int) -> bool:
        jugador = self.obtener_por_id(jugador_id)
        if jugador is None:
            return False
        self.session.delete(jugador)
        self.session.commit()
        return True

    def buscar_por_nombre(self, nombre: str, limit: int = 20) -> List[JugadorORM]:
        return (
            self.session.query(JugadorORM)
            .filter(JugadorORM.nombre.ilike(f"%{nombre}%"))
            .limit(limit)
            .all()
        )

    def contar(self) -> int:
        return self.session.query(JugadorORM).count()
