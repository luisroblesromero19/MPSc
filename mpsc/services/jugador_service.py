"""
MPSc — services/jugador_service.py
Servicio de negocio para gestión de jugadores.
Coordina repositorios y adaptadores.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from mpsc.database.connection import get_session
from mpsc.database.repositories.jugador_repository import JugadorRepository
from mpsc.database.repositories.temporada_repository import TemporadaRepository
from mpsc.database.adapters import orm_a_jugador, jugador_a_orm, jugador_a_temporada
from mpsc.database.models.jugador_model import JugadorORM
from mpsc.database.models.temporada_model import TemporadaORM
from mpsc.models.jugador import Jugador


class JugadorService:

    def __init__(self, session: Optional[Session] = None):
        self._session_own = session is None
        self.session = session or get_session()
        self.jugador_repo = JugadorRepository(self.session)
        self.temporada_repo = TemporadaRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_own:
            self.session.close()

    def crear_jugador(self, datos_base: dict) -> JugadorORM:
        jugador_orm = self.jugador_repo.crear(datos_base)
        return jugador_orm

    def obtener_jugador(self, jugador_id: int) -> Optional[Jugador]:
        orm = self.jugador_repo.obtener_por_id(jugador_id)
        if orm is None:
            return None
        ultima_temp = self.temporada_repo.obtener_ultima_por_jugador(jugador_id)
        return orm_a_jugador(orm, ultima_temp)

    def listar_jugadores(self, offset: int = 0, limit: int = 100) -> List[JugadorORM]:
        return self.jugador_repo.listar(offset, limit)

    def actualizar_jugador(self, jugador_id: int, datos: dict) -> Optional[JugadorORM]:
        return self.jugador_repo.actualizar(jugador_id, datos)

    def eliminar_jugador(self, jugador_id: int) -> bool:
        return self.jugador_repo.eliminar(jugador_id)

    def guardar_jugador_con_temporada(
        self, jugador: Jugador, temporada: str = ""
    ) -> tuple[JugadorORM, TemporadaORM]:
        orm_base = jugador_a_orm(jugador)
        jugador_orm = self.jugador_repo.crear({
            "nombre": orm_base.nombre,
            "fecha_nacimiento": orm_base.fecha_nacimiento,
            "edad": orm_base.edad,
            "pais_origen": orm_base.pais_origen,
            "ciudad_actual": orm_base.ciudad_actual,
            "idioma": orm_base.idioma,
            "experiencia_extranjero": orm_base.experiencia_extranjero,
            "valor_mercado": orm_base.valor_mercado,
            "posicion_principal": orm_base.posicion_principal,
        })
        temp_orm = jugador_a_temporada(jugador, temporada)
        temp_orm.jugador_id = jugador_orm.id
        self.session.add(temp_orm)
        self.session.commit()
        self.session.refresh(temp_orm)
        return jugador_orm, temp_orm

    def buscar_por_nombre(self, nombre: str, limit: int = 20) -> List[JugadorORM]:
        return self.jugador_repo.buscar_por_nombre(nombre, limit)

    def contar_jugadores(self) -> int:
        return self.jugador_repo.contar()
