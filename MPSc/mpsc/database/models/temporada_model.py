"""
MPSc — database/models/temporada_model.py
Modelo ORM para la tabla `temporadas_jugador`.
Almacena datos históricos de rendimiento por temporada.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..connection import Base


class TemporadaORM(Base):
    __tablename__ = "temporadas_jugador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jugador_id = Column(Integer, ForeignKey("jugadores.id", ondelete="CASCADE"), nullable=False, index=True)

    temporada = Column(String(20), default="", index=True)
    club_actual = Column(String(255), default="")
    liga = Column(String(50), default="")
    posicion_tabla = Column(Integer, default=0)
    total_equipos_liga = Column(Integer, default=0)
    tiene_copa = Column(Boolean, default=False)
    tiene_internacional = Column(Boolean, default=False)
    sistema_tactico_club = Column(String(100), default="")
    estilo_ofensivo = Column(String(100), default="")
    estilo_defensivo = Column(String(100), default="")
    estilo_transicion = Column(String(100), default="")
    altitud_ciudad = Column(Float, default=0.0)
    minutos_jugados = Column(Float, default=0.0)
    minutos_posibles = Column(Float, default=0.0)
    posicion = Column(String(50), default="", index=True)
    rol = Column(String(50), default="")
    estadisticas_json = Column(JSON, default=dict)
    num_lesiones = Column(Integer, default=0)
    tipo_lesion = Column(String(50), default="")
    semanas_baja_promedio = Column(Float, default=0.0)
    zonas_json = Column(JSON, default=list)
    sofascore_jugador_raw = Column(Text, default="")
    stats_club_origen_raw = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    jugador = relationship("JugadorORM", back_populates="temporadas")

    def __repr__(self):
        return f"<TemporadaORM(id={self.id}, jugador_id={self.jugador_id}, temporada='{self.temporada}')>"
