"""
MPSc — examples/demo_persistencia.py
Ejemplo de uso de la capa de persistencia.
Muestra cómo guardar y recuperar jugadores con su historial.

Uso: python examples/demo_persistencia.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from mpsc.database.connection import DatabaseManager, init_db
from mpsc.services.jugador_service import JugadorService
from mpsc.services.temporada_service import TemporadaService
from mpsc.models.jugador import Jugador


def demo():
    DatabaseManager.initialize()
    init_db()

    # -- 1. Crear un jugador con datos base --
    with JugadorService() as svc:
        datos = {
            "nombre": "Juan Pérez",
            "fecha_nacimiento": "1998-03-15",
            "edad": 26,
            "pais_origen": "México",
            "ciudad_actual": "Guadalajara",
            "idioma": "español",
            "experiencia_extranjero": False,
            "valor_mercado": "€5,000,000",
            "posicion_principal": "delantero_centro",
        }
        orm = svc.crear_jugador(datos)
        print(f"OK Jugador creado: id={orm.id}, nombre={orm.nombre}")

    # -- 2. Agregar temporada al jugador --
    jug = Jugador()
    jug.nombre = "Juan Pérez"
    jug.edad = 26
    jug.club_actual = "Club Deportivo Guadalajara"
    jug.liga = "liga_mx"
    jug.posicion_tabla = 5
    jug.total_equipos_liga = 18
    jug.tiene_copa = True
    jug.tiene_internacional = False
    jug.minutos_jugados = 2500
    jug.minutos_posibles = 3060
    jug.posicion = "delantero_centro"
    jug.rol = "titular_indiscutible"
    jug.estadisticas = {"goles": 15, "tiros": 60}
    jug.num_lesiones = 0
    jug.zonas = [14, 11, 8, 5, 2]
    jug.sofascore_jugador_raw = "partidos 34\ngoles 15\n"

    with TemporadaService() as svc:
        temp = svc.agregar_temporada(orm.id, jug, temporada="2025-2026")
        print(f"OK Temporada creada: id={temp.id}, temporada={temp.temporada}")

    # -- 3. Guardar jugador + temporada en un solo paso --
    jug2 = Jugador()
    jug2.nombre = "Carlos López"
    jug2.edad = 24
    jug2.club_actual = "Club América"
    jug2.liga = "liga_mx"
    jug2.posicion = "mediocampista_central"
    jug2.rol = "titular_indiscutible"
    jug2.minutos_jugados = 2700
    jug2.minutos_posibles = 3060

    with JugadorService() as svc:
        orm2, temp2 = svc.guardar_jugador_con_temporada(jug2, temporada="2025-2026")
        print(f"OK Jugador+temporada guardados: id={orm2.id}, temp_id={temp2.id}")

    # -- 4. Obtener jugador con su última temporada (como dataclass) --
    with JugadorService() as svc:
        jugador_dc = svc.obtener_jugador(orm.id)
        if jugador_dc:
            print(f"\n  Jugador recuperado: {jugador_dc.nombre}")
            print(f"  Edad: {jugador_dc.edad}")
            print(f"  Club actual: {jugador_dc.club_actual}")
            print(f"  Liga: {jugador_dc.liga}")
            print(f"  Posicion: {jugador_dc.posicion}")
            print(f"  Minutos: {jugador_dc.minutos_jugados}/{jugador_dc.minutos_posibles}")

    # -- 5. Listar jugadores --
    with JugadorService() as svc:
        todos = svc.listar_jugadores()
        print(f"\n  Total jugadores en BD: {len(todos)}")
        for j in todos:
            print(f"    [{j.id}] {j.nombre} ({j.posicion_principal})")

    # -- 6. Obtener historico de un jugador --
    with TemporadaService() as svc:
        historico = svc.obtener_historico(orm.id)
        print(f"\n  Historial de {orm.nombre}: {len(historico)} temporada(s)")
        for t in historico:
            print(f"    {t.temporada}: {t.club_actual} | {t.minutos_jugados} min | pos={t.posicion}")

    DatabaseManager.dispose()


if __name__ == "__main__":
    demo()
