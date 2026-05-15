"""
MPSc — database/adapters.py
Funciones adaptadoras entre ORM (JugadorORM, TemporadaORM)
y dataclasses del dominio (Jugador).
Mantiene compatibilidad con el motor de cálculo existente.
"""

from typing import Optional
from mpsc.models.jugador import Jugador
from .models.jugador_model import JugadorORM
from .models.temporada_model import TemporadaORM


def orm_a_jugador(orm: JugadorORM, ultima_temporada: Optional[TemporadaORM] = None) -> Jugador:
    j = Jugador()
    j.nombre = orm.nombre
    j.fecha_nacimiento = orm.fecha_nacimiento
    j.edad = orm.edad
    j.pais_origen = orm.pais_origen
    j.ciudad_actual = orm.ciudad_actual
    j.idioma = orm.idioma
    j.experiencia_extranjero = orm.experiencia_extranjero
    j.valor_mercado = orm.valor_mercado

    if ultima_temporada:
        j.club_actual = ultima_temporada.club_actual
        j.liga = ultima_temporada.liga
        j.posicion_tabla = ultima_temporada.posicion_tabla
        j.total_equipos_liga = ultima_temporada.total_equipos_liga
        j.tiene_copa = ultima_temporada.tiene_copa
        j.tiene_internacional = ultima_temporada.tiene_internacional
        j.sistema_tactico_club = ultima_temporada.sistema_tactico_club
        j.estilo_ofensivo = ultima_temporada.estilo_ofensivo
        j.estilo_defensivo = ultima_temporada.estilo_defensivo
        j.estilo_transicion = ultima_temporada.estilo_transicion
        j.altitud_ciudad = ultima_temporada.altitud_ciudad
        j.minutos_jugados = ultima_temporada.minutos_jugados
        j.minutos_posibles = ultima_temporada.minutos_posibles
        j.posicion = ultima_temporada.posicion
        j.rol = ultima_temporada.rol
        if ultima_temporada.estadisticas_json:
            j.estadisticas = dict(ultima_temporada.estadisticas_json)
        j.num_lesiones = ultima_temporada.num_lesiones
        j.tipo_lesion = ultima_temporada.tipo_lesion
        j.semanas_baja_promedio = ultima_temporada.semanas_baja_promedio
        if ultima_temporada.zonas_json:
            j.zonas = list(ultima_temporada.zonas_json)
        j.sofascore_jugador_raw = ultima_temporada.sofascore_jugador_raw
        j.stats_club_origen_raw = ultima_temporada.stats_club_origen_raw

    return j


def jugador_a_orm(jugador: Jugador) -> JugadorORM:
    return JugadorORM(
        nombre=jugador.nombre,
        fecha_nacimiento=jugador.fecha_nacimiento,
        edad=jugador.edad,
        pais_origen=jugador.pais_origen,
        ciudad_actual=jugador.ciudad_actual,
        idioma=jugador.idioma,
        experiencia_extranjero=jugador.experiencia_extranjero,
        valor_mercado=jugador.valor_mercado,
        posicion_principal=jugador.posicion,
    )


def jugador_a_temporada(jugador: Jugador, temporada: str = "") -> TemporadaORM:
    return TemporadaORM(
        temporada=temporada,
        club_actual=jugador.club_actual,
        liga=jugador.liga,
        posicion_tabla=jugador.posicion_tabla,
        total_equipos_liga=jugador.total_equipos_liga,
        tiene_copa=jugador.tiene_copa,
        tiene_internacional=jugador.tiene_internacional,
        sistema_tactico_club=jugador.sistema_tactico_club,
        estilo_ofensivo=jugador.estilo_ofensivo,
        estilo_defensivo=jugador.estilo_defensivo,
        estilo_transicion=jugador.estilo_transicion,
        altitud_ciudad=jugador.altitud_ciudad,
        minutos_jugados=jugador.minutos_jugados,
        minutos_posibles=jugador.minutos_posibles,
        posicion=jugador.posicion,
        rol=jugador.rol,
        estadisticas_json=dict(jugador.estadisticas) if jugador.estadisticas else None,
        num_lesiones=jugador.num_lesiones,
        tipo_lesion=jugador.tipo_lesion,
        semanas_baja_promedio=jugador.semanas_baja_promedio,
        zonas_json=list(jugador.zonas) if jugador.zonas else None,
        sofascore_jugador_raw=jugador.sofascore_jugador_raw,
        stats_club_origen_raw=jugador.stats_club_origen_raw,
    )
