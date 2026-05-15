"""
MPSc — modules/vectorizacion.py
Vectorización táctica de jugadores y clubes.
Genera vectores numéricos normalizados 0-1 para similitud coseno.
"""

import math
from typing import List, Optional
from mpsc.models.jugador import Jugador
from mpsc.modules.inferencia_tactica import PerfilTacticoClub


# ── Pesos por posición para inferir dimensiones tácticas desde stats ──
# Cada dimensión (0-1) se estima desde las estadísticas disponibles del jugador.

DIMENSIONES = [
    "finalizacion",
    "progresion",
    "amplitud",
    "recuperacion",
    "juego_aereo",
    "regate",
    "creatividad",
    "intensidad",
    "movilidad",
    "disciplina_tactica",
]


def _clamp01(valor: float) -> float:
    return max(0.0, min(1.0, valor))


def _ratio(num: float, den: float) -> float:
    if den <= 0:
        return 0.0
    return num / den


def generar_vector_jugador(jugador: Jugador) -> List[float]:
    """Genera un vector táctico de 10 dimensiones (0-1) para un jugador.

    Usa estadísticas disponibles + metadatos (posición, rol, minutos).
    Si faltan datos, usa valores por defecto basados en la posición.
    """
    est = jugador.estadisticas or {}
    pos = jugador.posicion.lower().strip()

    # ── FINALIZACIÓN ──
    goles = est.get("goles", 0)
    tiros = est.get("tiros", 1)
    if tiros <= 0:
        tiros = 1
    finalizacion = _clamp01(_ratio(goles, tiros) * 5.0)

    # ── PROGRESIÓN ──
    pases_prog = est.get("pases_prog", 0)
    total_pases = est.get("pases_comp", est.get("pases_int", 1))
    if total_pases <= 0:
        total_pases = 1
    progresion = _clamp01(_ratio(pases_prog, total_pases) * 10.0)

    # ── AMPLITUD ──
    centros = est.get("centros", 0)
    regates_int = est.get("regates_int", 0)
    amplitud = _clamp01((centros + regates_int) / 100.0)

    # ── RECUPERACIÓN ──
    recuperaciones = est.get("recuperaciones", 0)
    intercepciones = est.get("intercepciones", 0)
    recuperacion = _clamp01((recuperaciones + intercepciones) / 100.0)

    # ── JUEGO AÉREO ──
    da_ganados = est.get("da_ganados", 0)
    da_total = est.get("da_disputados", 1)
    if da_total <= 0:
        da_total = 1
    juego_aereo = _clamp01(_ratio(da_ganados, da_total) * 2.0)

    # ── REGATE ──
    regates_ok = est.get("regates_ok", 0)
    regates_int_total = est.get("regates_int", 1)
    if regates_int_total <= 0:
        regates_int_total = 1
    regate = _clamp01(_ratio(regates_ok, regates_int_total) * 2.0)

    # ── CREATIVIDAD ──
    pases_clave = est.get("pases_clave", 0)
    asistencias = est.get("asistencias", 0)
    creatividad = _clamp01((pases_clave + asistencias * 2) / 50.0)

    # ── INTENSIDAD ──
    entradas = est.get("entradas", 0)
    faltas_rec = est.get("faltas_rec", 0)
    intensidad = _clamp01((entradas + faltas_rec) / 80.0)

    # ── MOVILIDAD ──
    # Score basado en rol: más minutos = más movilidad/participación
    movilidad_map = {
        "titular_indiscutible": 0.9,
        "titular_con_competencia": 0.7,
        "rotacion_habitual": 0.5,
        "suplente": 0.3,
        "sin_minutos": 0.1,
    }
    movilidad = movilidad_map.get(jugador.rol, 0.5)

    # ── DISCIPLINA TÁCTICA ──
    # Inversamente proporcional a faltas cometidas y tarjetas
    # Proxy: a más lesiones por faltas, menos disciplina
    faltas = est.get("faltas", 0)
    disciplina_tactica = _clamp01(1.0 - faltas / 60.0)

    vector = [
        finalizacion,
        progresion,
        amplitud,
        recuperacion,
        juego_aereo,
        regate,
        creatividad,
        intensidad,
        movilidad,
        disciplina_tactica,
    ]

    return [round(v, 4) for v in vector]


def generar_vector_necesidad_club(
    perfil: PerfilTacticoClub,
    necesidades: list,
) -> List[float]:
    """Genera un vector de necesidad táctica del club (10 dim, 0-1).
    Compatible con generar_vector_jugador para similitud coseno.

    El vector representa qué perfil de jugador necesita el club:
    - Valores altos = alta necesidad de esa capacidad
    - Se basa en el perfil táctico + necesidades detectadas.
    """
    p = perfil

    # Mapeo de perfil táctico a necesidades por dimensión
    # Cada dimensión se deriva del perfil inverso: si al club le falta
    # algo (puntuación baja), la necesidad es alta.

    # finalizacion: si eficiencia_ofensiva es baja, necesitan finalizador
    finalizacion = _clamp01((10.0 - p.eficiencia_ofensiva) / 10.0)

    # progresion: si progresion baja, necesitan progresión
    progresion = _clamp01((10.0 - p.progresion) / 10.0)

    # amplitud: si amplitud baja, necesitan amplitud
    amplitud = _clamp01((10.0 - p.amplitud) / 10.0)

    # recuperacion: si intensidad_presion baja, necesitan recuperación
    recuperacion = _clamp01((10.0 - p.intensidad_presion) / 10.0)

    # juego_aereo: si fragilidad_aerea alta, necesitan juego aéreo
    juego_aereo = _clamp01(p.fragilidad_aerea / 10.0)

    # regate: si dependencia_bandas baja y amplitud baja, necesitan regate
    regate = _clamp01((10.0 - p.dependencia_bandas) / 10.0)

    # creatividad: si control_juego bajo, necesitan creatividad
    creatividad = _clamp01((10.0 - p.control_juego) / 10.0)

    # intensidad: si intensidad_presion baja, necesitan intensidad
    intensidad = _clamp01((10.0 - p.intensidad_presion) / 10.0)

    # movilidad: si verticalidad alta, necesitan movilidad
    movilidad = _clamp01(p.verticalidad / 10.0)

    # disciplina_tactica: si fragilidad_defensiva alta, necesitan disciplina
    disciplina_tactica = _clamp01(p.fragilidad_defensiva / 10.0)

    vector = [
        finalizacion,
        progresion,
        amplitud,
        recuperacion,
        juego_aereo,
        regate,
        creatividad,
        intensidad,
        movilidad,
        disciplina_tactica,
    ]

    return [round(v, 4) for v in vector]


def similitud_coseno(vec_a: List[float], vec_b: List[float]) -> float:
    """Similitud coseno entre dos vectores de igual dimensión."""
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Dimensiones diferentes: {len(vec_a)} vs {len(vec_b)}")
    prod = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return round(prod / (mag_a * mag_b), 4)


def compatibilidad_tactica(
    jugador: Jugador,
    perfil: PerfilTacticoClub,
    necesidades: list,
    minutos_participacion: Optional[float] = None,
    partidos_esperados: Optional[float] = None,
) -> dict:
    """Calcula la compatibilidad táctica entre un jugador y un club.

    Args:
        jugador: Dataclass del jugador.
        perfil: Perfil táctico inferido del club.
        necesidades: Lista de NecesidadTactica del club.
        minutos_participacion: Minutos jugados por el jugador (para confianza).
        partidos_esperados: Partidos esperados para normalizar confianza.

    Returns:
        Dict con score_tactico, confianza, fortalezas y riesgos.
    """
    vec_jug = generar_vector_jugador(jugador)
    vec_club = generar_vector_necesidad_club(perfil, necesidades)

    sim = similitud_coseno(vec_jug, vec_club)

    # Confianza estadística basada en minutos jugados
    mins = minutos_participacion or jugador.minutos_jugados
    ref = partidos_esperados or 900.0  # ~10 partidos completos
    if ref <= 0:
        ref = 900.0
    confianza = min(mins / ref, 1.0)

    # Score táctico final = similitud * confianza (penaliza muestras pequeñas)
    score_tactico = round(sim * confianza, 4)

    # Fortalezas: dimensiones donde el jugador supera la necesidad del club
    fortalezas = []
    for i, dim in enumerate(DIMENSIONES):
        if vec_jug[i] >= vec_club[i] and vec_jug[i] >= 0.6:
            fortalezas.append(dim)

    # Riesgos: dimensiones donde el jugador no alcanza la necesidad
    riesgos = []
    for i, dim in enumerate(DIMENSIONES):
        if vec_jug[i] < vec_club[i] and (vec_club[i] - vec_jug[i]) >= 0.3:
            riesgos.append(dim)

    # Necesidades cubiertas
    necesidades_cubiertas = []
    for nec in necesidades:
        dim_map = {
            "delantero_centro": "finalizacion",
            "mediocampista_central": "creatividad",
            "central": "juego_aereo",
            "extremo": "amplitud",
            "lateral": "amplitud",
            "mediocampista_defensivo": "recuperacion",
        }
        dim = dim_map.get(nec.rol, "")
        if dim and dim in fortalezas:
            necesidades_cubiertas.append(nec.rol)

    return {
        "score_tactico": score_tactico,
        "similitud": round(sim, 4),
        "confianza": round(confianza, 4),
        "fortalezas": fortalezas,
        "riesgos": riesgos,
        "necesidades_cubiertas": necesidades_cubiertas,
        "vector_jugador": vec_jug,
        "vector_necesidad": vec_club,
    }
