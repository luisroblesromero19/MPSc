"""
MPSc — examples/demo_scouting_automatico.py
Demo completa de scouting automático.

Flujo:
1. Crear club desde estadísticas
2. Inferir perfil táctico automáticamente
3. Detectar necesidades del club
4. Buscar jugadores compatibles en BD
5. Mostrar ranking final explicado
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from mpsc.database.connection import DatabaseManager, init_db
from mpsc.services.club_service import ClubService
from mpsc.services.jugador_service import JugadorService
from mpsc.services.scouting_service import ScoutingService
from mpsc.modules.inferencia_tactica import inferir_perfil, PerfilTacticoClub
from mpsc.modules.detector_necesidades import DetectorNecesidades
from mpsc.modules.vectorizacion import (
    generar_vector_jugador, generar_vector_necesidad_club,
    similitud_coseno, compatibilidad_tactica,
)
from mpsc.models.jugador import Jugador


def setup_datos():
    """Crea datos de ejemplo: club + jugadores históricos."""
    with ClubService() as svc:
        club = svc.crear_club({
            "nombre": "Club Deportivo Guadalajara",
            "pais": "México",
            "liga": "liga_mx",
            "division": "primera",
            "temporada_actual": "2025-2026",
            "entrenador": "Óscar García",
            "sistema_tactico": "4-3-3",
        })

        stats_club = {
            "temporada": "2025-2026",
            "partidos": 34,
            "goles_favor": 45,
            "goles_contra": 38,
            "asistencias": 30,
            "posesion": 48.5,
            "pases_precisos": 14200,
            "precision_pases": 76.2,
            "balones_largos": 680,
            "precision_balones_largos": 58.0,
            "centros": 420,
            "precision_centros": 28.5,
            "regates": 310,
            "corners": 165,
            "tiros": 420,
            "tiros_puerta": 155,
            "porterias_cero": 8,
            "intercepciones": 420,
            "recuperaciones": 1480,
            "errores_tiro": 85,
            "duelos_ganados": 980,
            "duelos_aereos": 520,
            "fueras_juego": 45,
            "faltas": 380,
            "amarillas": 55,
            "rojas": 2,
        }
        svc.agregar_temporada(club.id, stats_club)
        print(f"  Club creado: id={club.id}, nombre={club.nombre}")

    with JugadorService() as svc:
        jugadores_data = [
            {
                "nombre": "Carlos Vela",
                "posicion_principal": "delantero_centro",
                "club_actual": "LAFC",
                "liga": "mls",
                "edad": 31,
                "pais_origen": "México",
                "goles": 18, "tiros": 85, "pases_prog": 120,
                "pases_comp": 850, "centros": 60, "regates_int": 95,
                "recuperaciones": 180, "intercepciones": 25,
                "da_ganados": 35, "da_disputados": 80,
                "regates_ok": 50, "pases_clave": 45,
                "asistencias": 8, "entradas": 30, "faltas_rec": 25,
                "minutos": 2500, "posicion": "delantero_centro",
                "rol": "titular_indiscutible",
            },
            {
                "nombre": "Edson Álvarez",
                "posicion_principal": "mediocampista_defensivo",
                "club_actual": "West Ham",
                "liga": "premier_league",
                "edad": 27,
                "pais_origen": "México",
                "goles": 3, "tiros": 30, "pases_prog": 280,
                "pases_comp": 1200, "centros": 10, "regates_int": 25,
                "recuperaciones": 350, "intercepciones": 80,
                "da_ganados": 60, "da_disputados": 100,
                "regates_ok": 15, "pases_clave": 20,
                "asistencias": 2, "entradas": 85, "faltas_rec": 40,
                "minutos": 2700, "posicion": "mediocampista_defensivo",
                "rol": "titular_indiscutible",
            },
            {
                "nombre": "Santi Giménez",
                "posicion_principal": "delantero_centro",
                "club_actual": "Feyenoord",
                "liga": "eredivisie",
                "edad": 24,
                "pais_origen": "México",
                "goles": 15, "tiros": 55, "pases_prog": 90,
                "pases_comp": 600, "centros": 20, "regates_int": 50,
                "recuperaciones": 120, "intercepciones": 15,
                "da_ganados": 45, "da_disputados": 75,
                "regates_ok": 28, "pases_clave": 25,
                "asistencias": 5, "entradas": 20, "faltas_rec": 30,
                "minutos": 2000, "posicion": "delantero_centro",
                "rol": "titular_indiscutible",
            },
            {
                "nombre": "Luis Chávez",
                "posicion_principal": "mediocampista_central",
                "club_actual": "Dinamo Moscú",
                "liga": "rusa",
                "edad": 28,
                "pais_origen": "México",
                "goles": 6, "tiros": 40, "pases_prog": 320,
                "pases_comp": 1400, "centros": 85, "regates_int": 40,
                "recuperaciones": 280, "intercepciones": 55,
                "da_ganados": 30, "da_disputados": 65,
                "regates_ok": 22, "pases_clave": 55,
                "asistencias": 7, "entradas": 45, "faltas_rec": 35,
                "minutos": 2400, "posicion": "mediocampista_central",
                "rol": "titular_indiscutible",
            },
            {
                "nombre": "Julián Quiñones",
                "posicion_principal": "delantero_centro",
                "club_actual": "Al Qadsiah",
                "liga": "saudi",
                "edad": 29,
                "pais_origen": "México",
                "goles": 12, "tiros": 65, "pases_prog": 110,
                "pases_comp": 700, "centros": 45, "regates_int": 75,
                "recuperaciones": 140, "intercepciones": 20,
                "da_ganados": 25, "da_disputados": 60,
                "regates_ok": 40, "pases_clave": 30,
                "asistencias": 6, "entradas": 25, "faltas_rec": 28,
                "minutos": 2100, "posicion": "delantero_centro",
                "rol": "titular_con_competencia",
            },
        ]

        for jd in jugadores_data:
            jug = Jugador()
            jug.nombre = jd["nombre"]
            jug.edad = jd["edad"]
            jug.pais_origen = jd["pais_origen"]
            jug.club_actual = jd["club_actual"]
            jug.liga = jd["liga"]
            jug.posicion = jd["posicion"]
            jug.rol = jd["rol"]
            jug.minutos_jugados = float(jd["minutos"])
            jug.minutos_posibles = 3060.0
            jug.estadisticas = {
                "goles": jd["goles"], "tiros": jd["tiros"],
                "pases_prog": jd["pases_prog"], "pases_comp": jd["pases_comp"],
                "centros": jd["centros"], "regates_int": jd["regates_int"],
                "recuperaciones": jd["recuperaciones"], "intercepciones": jd["intercepciones"],
                "da_ganados": jd["da_ganados"], "da_disputados": jd["da_disputados"],
                "regates_ok": jd["regates_ok"], "pases_clave": jd["pases_clave"],
                "asistencias": jd["asistencias"], "entradas": jd["entradas"],
                "faltas_rec": jd["faltas_rec"],
            }

            orm, _ = svc.guardar_jugador_con_temporada(jug, "2025-2026")
            print(f"  Jugador creado: id={orm.id}, {orm.nombre} ({jd['posicion_principal']})")

        return club.id


def mostrar_perfil(perfil: PerfilTacticoClub):
    print("\n  PERFIL TACTICO DEL CLUB:")
    for attr in [
        "amplitud", "verticalidad", "posesion", "intensidad_presion",
        "agresividad_defensiva", "dependencia_bandas", "progresion",
        "control_juego", "fragilidad_defensiva", "fragilidad_aerea",
        "eficiencia_ofensiva", "volumen_ofensivo",
    ]:
        val = getattr(perfil, attr)
        barra = "█" * int(val) + "░" * (10 - int(val))
        print(f"    {attr:25s} {barra} {val:.1f}")


def mostrar_necesidades(necesidades):
    print(f"\n  NECESIDADES DETECTADAS ({len(necesidades)}):")
    for n in necesidades:
        barra = "█" * int(n.prioridad * 10) + "░" * (10 - int(n.prioridad * 10))
        print(f"    {n.rol:35s} [{barra}] {n.prioridad:.2f}  {n.motivo}")


def mostrar_ranking(resultados, limit=5):
    print(f"\n  RANKING DE JUGADORES COMPATIBLES (top {limit}):")
    print(f"  {'#':>3s}  {'Jugador':25s}  {'Posición':22s}  {'Score':>6s}  {'Confianza':>9s}  {'Fortalezas':30s}  {'Necesidades Cubiertas':25s}")
    print("  " + "─" * 130)
    for i, r in enumerate(resultados[:limit], 1):
        fort = ", ".join(r.fortalezas_detectadas[:3]) if r.fortalezas_detectadas else "-"
        nec_cub = ", ".join(r.necesidades_cubiertas) if r.necesidades_cubiertas else "-"
        print(f"  {i:3d}  {r.jugador.nombre:25s}  {r.jugador.posicion:22s}  {r.score_compatibilidad:6.3f}  {r.confianza_estadistica:9.3f}  {fort:30s}  {nec_cub:25s}")


def demo():
    DatabaseManager.initialize()
    init_db()

    print("=" * 70)
    print("FASE 2 — SCOUTING AUTOMATICO")
    print("=" * 70)

    # ── 1. Setup: crear club + jugadores ──
    print("\n[1] Creando datos de ejemplo...")
    club_id = setup_datos()

    # ── 2. Inferir perfil táctico ──
    print("\n[2] Infiriendo perfil táctico del club...")
    with ClubService() as svc:
        temp = svc.obtener_ultima_temporada(club_id)
        stats = {c.name: getattr(temp, c.name) for c in temp.__table__.columns}
        perfil = inferir_perfil(stats, temp.partidos)
        mostrar_perfil(perfil)

    # ── 3. Detectar necesidades ──
    print("\n[3] Detectando necesidades...")
    detector = DetectorNecesidades()
    necesidades = detector.detectar(perfil)
    mostrar_necesidades(necesidades)

    # ── 4. Buscar jugadores compatibles ──
    print("\n[4] Buscando jugadores compatibles...")
    with ScoutingService() as svc:
        resultados = svc.buscar_jugadores_compatibles(
            club_id, limit=10, filtros=None
        )
        mostrar_ranking(resultados)

    # ── 5. Mostrar compatibilidad táctica detallada del #1 ──
    if resultados:
        print("\n[5] Desglose del mejor candidato:")
        r = resultados[0]
        print(f"\n  Jugador: {r.jugador.nombre}")
        print(f"  Posición: {r.jugador.posicion}")
        print(f"  Club actual: {r.jugador.club_actual}")
        print(f"  Score compatibilidad: {r.score_compatibilidad:.4f}")
        print(f"  Confianza estadística: {r.confianza_estadistica:.4f}")
        print(f"  Fortalezas: {', '.join(r.fortalezas_detectadas)}")
        print(f"  Riesgos: {', '.join(r.riesgos_detectados)}")
        print(f"  Necesidades cubiertas: {', '.join(r.necesidades_cubiertas)}")

    print("\n" + "=" * 70)
    print("DEMO COMPLETADA")
    print("=" * 70)

    DatabaseManager.dispose()


if __name__ == "__main__":
    demo()
