"""
MPSc — utils/formulario_club.py
Formulario interactivo para capturar todos los datos del club destino.
"""
from config import COEFICIENTES_LIGA, POSICIONES
from models.club import Club
from utils.input_helper import (
    titulo, seccion, ok, warn, pedir_float, pedir_int,
    pedir_texto, pedir_sino, pedir_opcion, pedir_zonas,
    pedir_score_interpretativo,
)


def capturar_club() -> Club:
    c = Club()

    titulo("DATOS DEL CLUB DESTINO")

    # ── Identificación ───────────────────────────────────────────
    seccion("Identificación")
    c.nombre  = pedir_texto("Nombre del club:")
    c.ciudad  = pedir_texto("Ciudad:")
    c.pais    = pedir_texto("País:")
    c.idioma  = pedir_texto("Idioma oficial del club:")
    c.altitud = pedir_float("Altitud de la ciudad (metros):", 0.0)

    # ── Situación deportiva ───────────────────────────────────────
    seccion("Situación deportiva actual")

    ligas = list(COEFICIENTES_LIGA.keys())
    etiquetas_ligas = [f"{l.replace('_', ' ').title()} (coef. {v})"
                       for l, v in COEFICIENTES_LIGA.items()]
    c.liga = pedir_opcion("Liga del club:", ligas, etiquetas_ligas)

    c.posicion_tabla     = pedir_int("Posición actual en la tabla:", 1, 30)
    c.total_equipos_liga = pedir_int("Total de equipos en la liga:", 2, 30)

    print("\n  Forma reciente — últimas 5 jornadas:")
    c.victorias_recientes = pedir_int("  Victorias:", 0, 5)
    c.empates_recientes   = pedir_int("  Empates:",   0, 5)
    c.derrotas_recientes  = pedir_int("  Derrotas:",  0, 5)

    c.tiene_copa          = pedir_sino("¿El club participa en copa nacional?")
    c.tiene_internacional = pedir_sino("¿El club participa en torneo internacional?")

    # ── Modelo de juego ───────────────────────────────────────────
    seccion("Modelo de juego")
    c.sistema_tactico  = pedir_texto("Sistema táctico (ej: 4-3-3):")
    c.estilo_ofensivo  = pedir_texto("Estilo en fase ofensiva:")
    c.estilo_defensivo = pedir_texto("Estilo en fase defensiva:")
    c.estilo_transicion= pedir_texto("Estilo en fase de transición:")

    # ── Necesidad técnico-táctica ─────────────────────────────────
    seccion("Necesidad técnico-táctica")
    c.posicion_requerida = pedir_opcion(
        "Posición que necesita cubrir:",
        POSICIONES,
        [p.replace("_", " ").title() for p in POSICIONES],
    )
    c.perfil_tactico = pedir_texto(
        "Perfil táctico específico (ej: '9 móvil que baje a asociarse'):"
    )

    seccion("Zonas a cubrir por el nuevo jugador")
    c.zonas_requeridas = pedir_zonas("zonas requeridas por el club")
    ok(f"Zonas requeridas: {c.zonas_requeridas}")

    # ── Estado de la plantilla ─────────────────────────────────────
    seccion("Estado de la plantilla")
    c.jugadores_en_posicion   = pedir_int("¿Cuántos jugadores cubren actualmente esa posición?", 0, 10)
    c.pct_minutos_proyectados = pedir_float("Porcentaje de minutos proyectados para el fichaje (0-100):", 0.0, 100.0)
    ok(f"Saturación: {c.jugadores_en_posicion} jugadores | Minutos proyectados: {c.pct_minutos_proyectados:.0f}%")

    # ── Proyecto deportivo ─────────────────────────────────────────
    seccion("Proyecto deportivo")
    c.horizonte_anios  = pedir_int("Horizonte temporal del proyecto (años):", 1, 10)
    c.modo_competitivo = pedir_opcion(
        "Modo competitivo actual:",
        ["resultados_inmediatos", "consolidacion", "desarrollo"],
        ["Resultados inmediatos (ganar ya)", "Consolidación (crecer con estabilidad)",
         "Desarrollo (apostar por talento joven)"],
    )

    # ── Umbrales estadísticos ──────────────────────────────────────
    seccion("Umbrales estadísticos requeridos")
    print("  Ingresa el score mínimo esperado (1-10) para las métricas clave")
    print("  de la posición requerida. Deja en 0 si no aplica.\n")

    metricas_umbral = {
        "portero":                 ["save_pct", "gc_90", "salvadas_90", "pases_pct"],
        "central":                 ["da_pct", "dt_pct", "despejes_90", "pases_prog_90", "pases_pct"],
        "lateral":                 ["centros_pct", "pases_prog_90", "carreras_prog_90", "do_pct"],
        "mediocampista_defensivo": ["recuperaciones_90", "intercepciones_90", "pases_prog_90"],
        "mediocampista_central":   ["pases_clave_90", "pases_prog_90", "xg_90", "xa_90"],
        "extremo":                 ["xg_90", "regates_pct", "tiros_90", "xa_90"],
        "delantero_centro":        ["goles_90", "xg_90", "tiros_puerta_90", "pases_pct"],
    }

    for metrica in metricas_umbral.get(c.posicion_requerida, []):
        val = pedir_float(f"  Umbral mínimo para '{metrica}' (1-10, 0=no aplica): ", 0.0, 10.0)
        if val > 0:
            c.umbrales_estadisticos[metrica] = val

    # ── Módulos interpretativos ────────────────────────────────────
    seccion("Evaluación interpretativa del scout")
    warn("Los siguientes scores requieren criterio analítico del scout (1-10).\n")

    c.compat_tactica_ofensiva = pedir_score_interpretativo(
        "Compatibilidad táctica — Fase ofensiva",
        "¿Qué tan similar es la fase ofensiva del club origen del jugador con la del club destino?",
    )
    c.compat_tactica_defensiva = pedir_score_interpretativo(
        "Compatibilidad táctica — Fase defensiva",
        "¿Qué tan similar es la fase defensiva del club origen con la del club destino?",
    )
    c.compat_tactica_transicion = pedir_score_interpretativo(
        "Compatibilidad táctica — Transición",
        "¿Qué tan similares son los principios de transición de ambos clubes?",
    )
    c.alineacion_edad_horizonte = pedir_score_interpretativo(
        "Alineación edad-horizonte",
        "¿La edad del jugador encaja con el horizonte temporal del proyecto del club?",
    )
    c.alineacion_perfil_modo = pedir_score_interpretativo(
        "Alineación perfil-modo competitivo",
        "¿El perfil del jugador se alinea con el modo competitivo actual del club?",
    )
    c.proyeccion_continuidad = pedir_score_interpretativo(
        "Proyección de continuidad",
        "¿Es viable una renovación o continuidad a largo plazo con este jugador?",
    )

    return c
