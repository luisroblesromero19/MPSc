"""
MPSc — database/models/jugador_model.py
Modelo ORM para la tabla `jugadores`.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from ..connection import Base


class JugadorORM(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, index=True)
    fecha_nacimiento = Column(String(10), default="")
    edad = Column(Integer, default=0)
    pais_origen = Column(String(100), default="")
    ciudad_actual = Column(String(255), default="")
    idioma = Column(String(100), default="")
    experiencia_extranjero = Column(Boolean, default=False)
    valor_mercado = Column(String(100), default="")
    posicion_principal = Column(String(50), default="", index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    temporadas = relationship("TemporadaORM", back_populates="jugador", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JugadorORM(id={self.id}, nombre='{self.nombre}')>"
