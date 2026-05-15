"""
MPSc — modules/inferencia_tactica.py
Perfil Táctico Automático del Club.
Convierte estadísticas crudas del club en un perfil táctico estructurado
con atributos normalizados en rango 0-10.

Todas las fórmulas son heurísticas interpretables, configurables vía constantes.
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ── Constantes de normalización ──────────────────────────────────
# Valores de referencia por 90 minutos para escalar cada métrica a 0-10.
# Se asume que el club juega en una liga promedio (liga_mx como base).
REF_POSESION = 55.0        # posesion % -> 10
REF_PASES_PCT = 82.0       # precision pases % -> 10
REF_CENTROS_PARTIDO = 15.0 # centros por partido -> 10
REF_REGATES_PARTIDO = 12.0 # regates por partido -> 10
REF_CORNERS_PARTIDO = 6.0  # corners por partido -> 10
REF_BALONES_LARGOS = 25.0  # balones largos por partido -> 10
REF_FUERAS_JUEGO = 3.0     # fueras de juego por partido -> 10
REF_GOLES_CONTRA = 2.0     # goles contra por partido (inverso) -> 0 si = ref
REF_ERRORES_TIRO = 3.0     # errores por partido (inverso)
REF_RECUPERACIONES = 50.0  # recuperaciones por partido -> 10
REF_INTERCEPCIONES = 15.0  # intercepciones por partido -> 10
REF_GOLES_FAVOR = 2.0      # goles favor por partido -> 10
REF_TIROS_PARTIDO = 15.0   # tiros por partido -> 10
REF_DUELOS_AEREOS = 20.0   # duelos aéreos por partido -> 10


def _a_10(valor: float, referencia: float, inverso: bool = False) -> float:
    """Normaliza un valor a escala 0-10 dada una referencia.
    Si inverso=True, valores altos producen score bajo."""
    if referencia <= 0:
        return 5.0
    raw = (valor / referencia) * 10.0 if not inverso else (1.0 - valor / (referencia * 2))
    return max(0.0, min(10.0, round(raw, 2)))


def _por_partido(valor: float, partidos: int) -> float:
    """Convierte estadística total a valor por partido."""
    if partidos <= 0:
        return 0.0
    return valor / partidos


@dataclass
class PerfilTacticoClub:
    """Perfil táctico inferido de un club a partir de sus estadísticas.
    Todos los atributos en rango 0-10."""

    amplitud: float = 5.0
    verticalidad: float = 5.0
    posesion: float = 5.0
    intensidad_presion: float = 5.0
    agresividad_defensiva: float = 5.0
    dependencia_bandas: float = 5.0
    progresion: float = 5.0
    control_juego: float = 5.0
    fragilidad_defensiva: float = 5.0
    fragilidad_aerea: float = 5.0
    eficiencia_ofensiva: float = 5.0
    volumen_ofensivo: float = 5.0

    metricas_fuente: dict = field(default_factory=dict)

    def a_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, float)}

    def a_vector(self) -> list[float]:
        """Vector de 12 dimensiones para similitud coseno."""
        return [
            self.amplitud, self.verticalidad, self.posesion,
            self.intensidad_presion, self.agresividad_defensiva,
            self.dependencia_bandas, self.progresion, self.control_juego,
            self.fragilidad_defensiva, self.fragilidad_aerea,
            self.eficiencia_ofensiva, self.volumen_ofensivo,
        ]


def inferir_perfil(stats: dict, partidos: Optional[int] = None) -> PerfilTacticoClub:
    """Infiero el perfil táctico de un club desde sus estadísticas crudas.

    Args:
        stats: Diccionario con claves del TemporadaClubORM.
        partidos: Número de partidos (si no está en stats).

    Returns:
        PerfilTacticoClub con atributos 0-10.
    """
    p = partidos or stats.get("partidos", 1)
    if p <= 0:
        p = 1

    pp = _por_partido

    # ── AMPLITUD ──
    # Equipos que usan centros, regates y corners juegan más abiertos
    centros_pp = pp(stats.get("centros", 0), p)
    regates_pp = pp(stats.get("regates", 0), p)
    corners_pp = pp(stats.get("corners", 0), p)
    amplitud_raw = (centros_pp / REF_CENTROS_PARTIDO * 4 +
                    regates_pp / REF_REGATES_PARTIDO * 3 +
                    corners_pp / REF_CORNERS_PARTIDO * 3)
    amplitud = max(0.0, min(10.0, round(amplitud_raw, 2)))

    # ── VERTICALIDAD ──
    # Balones largos + fueras de juego indican juego directo/vertical
    bl_pp = pp(stats.get("balones_largos", 0), p)
    fj_pp = pp(stats.get("fueras_juego", 0), p)
    verticalidad_raw = (bl_pp / REF_BALONES_LARGOS * 6 +
                        fj_pp / REF_FUERAS_JUEGO * 4)
    verticalidad = max(0.0, min(10.0, round(verticalidad_raw, 2)))

    # ── POSESIÓN ──
    posesion = _a_10(stats.get("posesion", 50.0), REF_POSESION)

    # ── CONTROL DE JUEGO ──
    # Posesión + precisión de pases
    pases_pct = stats.get("precision_pases", 75.0)
    ctrl_jug_raw = (_a_10(stats.get("posesion", 50.0), REF_POSESION) * 0.5 +
                    _a_10(pases_pct, REF_PASES_PCT) * 0.5)
    control_juego = max(0.0, min(10.0, round(ctrl_jug_raw, 2)))

    # ── INTENSIDAD DE PRESIÓN ──
    # Recuperaciones + intercepciones
    rec_pp = pp(stats.get("recuperaciones", 0), p)
    int_pp = pp(stats.get("intercepciones", 0), p)
    presion_raw = (rec_pp / REF_RECUPERACIONES * 6 +
                   int_pp / REF_INTERCEPCIONES * 4)
    intensidad_presion = max(0.0, min(10.0, round(presion_raw, 2)))

    # ── AGRESIVIDAD DEFENSIVA ──
    # Faltas + amarillas + rojas indican intensidad defensiva
    faltas_pp = pp(stats.get("faltas", 0), p)
    amarillas_pp = pp(stats.get("amarillas", 0), p)
    rojas_pp = pp(stats.get("rojas", 0), p)
    agresividad_raw = (faltas_pp * 0.4 + amarillas_pp * 0.4 + rojas_pp * 2.0)
    agresividad_defensiva = max(0.0, min(10.0, round(agresividad_raw, 2)))

    # ── DEPENDENCIA DE BANDAS ──
    # Similar a amplitud pero ponderando más centros vs juego interior
    dep_bandas_raw = (centros_pp / REF_CENTROS_PARTIDO * 6 +
                      regates_pp / REF_REGATES_PARTIDO * 2 +
                      corners_pp / REF_CORNERS_PARTIDO * 2)
    dependencia_bandas = max(0.0, min(10.0, round(dep_bandas_raw, 2)))

    # ── PROGRESIÓN ──
    # Pases precisos como proxy de circulación progresiva
    pases_pp = pp(stats.get("pases_precisos", 0), p)
    progresion = _a_10(pases_pp / 100, 5.0)

    # ── FRAGILIDAD DEFENSIVA ──
    # Goles contra + errores de tiro (inverso: más goles/errores = más frágil)
    gc_pp = pp(stats.get("goles_contra", 0), p)
    err_pp = pp(stats.get("errores_tiro", 0), p)
    frag_def_raw = ((gc_pp / REF_GOLES_CONTRA) * 6 +
                    (err_pp / REF_ERRORES_TIRO) * 4)
    fragilidad_defensiva = max(0.0, min(10.0, round(frag_def_raw, 2)))

    # ── FRAGILIDAD AÉREA (inversa) ──
    # Pocos duelos aéreos ganados = fragilidad alta
    da_pp = pp(stats.get("duelos_aereos", 0), p)
    frag_aerea = _a_10(da_pp, REF_DUELOS_AEREOS, inverso=True)

    # ── EFICIENCIA OFENSIVA ──
    # Goles / Tiros = tasa de conversión
    tiros_total = stats.get("tiros", 1)
    if tiros_total <= 0:
        tiros_total = 1
    conversion = (stats.get("goles_favor", 0) / tiros_total) * 100
    eficiencia_ofensiva = max(0.0, min(10.0, round(conversion * 2, 2)))

    # ── VOLUMEN OFENSIVO ──
    # Tiros + tiros a puerta por partido
    tiros_pp_value = pp(stats.get("tiros", 0), p)
    tp_pp = pp(stats.get("tiros_puerta", 0), p)
    vol_raw = (tiros_pp_value / REF_TIROS_PARTIDO * 6 +
               tp_pp / (REF_TIROS_PARTIDO * 0.5) * 4)
    volumen_ofensivo = max(0.0, min(10.0, round(vol_raw, 2)))

    return PerfilTacticoClub(
        amplitud=amplitud,
        verticalidad=verticalidad,
        posesion=posesion,
        intensidad_presion=intensidad_presion,
        agresividad_defensiva=agresividad_defensiva,
        dependencia_bandas=dependencia_bandas,
        progresion=progresion,
        control_juego=control_juego,
        fragilidad_defensiva=fragilidad_defensiva,
        fragilidad_aerea=frag_aerea,
        eficiencia_ofensiva=eficiencia_ofensiva,
        volumen_ofensivo=volumen_ofensivo,
        metricas_fuente={
            "centros_pp": round(centros_pp, 2),
            "regates_pp": round(regates_pp, 2),
            "corners_pp": round(corners_pp, 2),
            "bl_pp": round(bl_pp, 2),
            "fj_pp": round(fj_pp, 2),
            "posesion": stats.get("posesion", 0),
            "pases_pct": pases_pct,
            "rec_pp": round(rec_pp, 2),
            "int_pp": round(int_pp, 2),
            "gc_pp": round(gc_pp, 2),
            "err_pp": round(err_pp, 2),
            "conversion_pct": round(conversion, 2),
            "tiros_pp": round(tiros_pp_value, 2),
        },
    )
