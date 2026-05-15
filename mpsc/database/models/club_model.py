"""
MPSc — database/models/club_model.py
Modelo ORM para la tabla `clubes`.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from ..connection import Base


class ClubORM(Base):
    __tablename__ = "clubes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, index=True)
    pais = Column(String(100), default="")
    liga = Column(String(50), default="", index=True)
    division = Column(String(50), default="")
    temporada_actual = Column(String(20), default="")
    entrenador = Column(String(255), default="")
    sistema_tactico = Column(String(100), default="")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    temporadas = relationship("TemporadaClubORM", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClubORM(id={self.id}, nombre='{self.nombre}')>"
