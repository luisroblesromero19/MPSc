"""
MPSc — database/models/temporada_club_model.py
Modelo ORM para la tabla `temporadas_club`.
Almacena datos estadísticos agregados del club por temporada.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from ..connection import Base


class TemporadaClubORM(Base):
    __tablename__ = "temporadas_club"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubes.id", ondelete="CASCADE"), nullable=False, index=True)

    temporada = Column(String(20), default="", index=True)
    partidos = Column(Integer, default=0)
    goles_favor = Column(Integer, default=0)
    goles_contra = Column(Integer, default=0)
    asistencias = Column(Integer, default=0)
    posesion = Column(Float, default=0.0)
    pases_precisos = Column(Integer, default=0)
    precision_pases = Column(Float, default=0.0)
    balones_largos = Column(Integer, default=0)
    precision_balones_largos = Column(Float, default=0.0)
    centros = Column(Integer, default=0)
    precision_centros = Column(Float, default=0.0)
    regates = Column(Integer, default=0)
    corners = Column(Integer, default=0)
    tiros = Column(Integer, default=0)
    tiros_puerta = Column(Integer, default=0)
    porterias_cero = Column(Integer, default=0)
    intercepciones = Column(Integer, default=0)
    recuperaciones = Column(Integer, default=0)
    errores_tiro = Column(Integer, default=0)
    duelos_ganados = Column(Integer, default=0)
    duelos_aereos = Column(Integer, default=0)
    fueras_juego = Column(Integer, default=0)
    faltas = Column(Integer, default=0)
    amarillas = Column(Integer, default=0)
    rojas = Column(Integer, default=0)
    sofascore_raw = Column(JSON, default=dict)

    metricas_ofensivas_json = Column(JSON, default=dict)
    metricas_defensivas_json = Column(JSON, default=dict)
    metricas_transicion_json = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("ClubORM", back_populates="temporadas")

    def __repr__(self):
        return f"<TemporadaClubORM(id={self.id}, club_id={self.club_id}, temporada='{self.temporada}')>"
