"""
MPSc — database/repositories/club_repository.py
CRUD completo para la entidad ClubORM.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.club_model import ClubORM


class ClubRepository:

    def __init__(self, session: Session):
        self.session = session

    def crear(self, datos: dict) -> ClubORM:
        club = ClubORM(**datos)
        self.session.add(club)
        self.session.commit()
        self.session.refresh(club)
        return club

    def obtener_por_id(self, club_id: int) -> Optional[ClubORM]:
        return self.session.query(ClubORM).filter(ClubORM.id == club_id).first()

    def listar(self, offset: int = 0, limit: int = 100) -> List[ClubORM]:
        return (
            self.session.query(ClubORM)
            .order_by(ClubORM.nombre)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def actualizar(self, club_id: int, datos: dict) -> Optional[ClubORM]:
        club = self.obtener_por_id(club_id)
        if club is None:
            return None
        for clave, valor in datos.items():
            if hasattr(club, clave):
                setattr(club, clave, valor)
        self.session.commit()
        self.session.refresh(club)
        return club

    def eliminar(self, club_id: int) -> bool:
        club = self.obtener_por_id(club_id)
        if club is None:
            return False
        self.session.delete(club)
        self.session.commit()
        return True

    def buscar_por_nombre(self, nombre: str, limit: int = 20) -> List[ClubORM]:
        return (
            self.session.query(ClubORM)
            .filter(ClubORM.nombre.ilike(f"%{nombre}%"))
            .limit(limit)
            .all()
        )

    def buscar_por_liga(self, liga: str, limit: int = 50) -> List[ClubORM]:
        return (
            self.session.query(ClubORM)
            .filter(ClubORM.liga == liga)
            .limit(limit)
            .all()
        )

    def contar(self) -> int:
        return self.session.query(ClubORM).count()
