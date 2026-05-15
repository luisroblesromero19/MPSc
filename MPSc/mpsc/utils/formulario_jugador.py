"""
MPSc — utils/formulario_jugador.py
Formulario interactivo para capturar todos los datos del jugador.
"""
from config import COEFICIENTES_LIGA, POSICIONES, METRICAS_POR_POSICION
from models.jugador import Jugador
from utils.input_helper import (
    titulo, seccion, ok, warn, pedir_float, pedir_int,
    pedir_texto, pedir_sino, pedir_opcion, pedir_zonas,
)


def capturar_jugador() -> Jugador:
    j = Jugador()

    titulo("DATOS DEL JUGADOR")

    # ── Identificación ───────────────────────────────────────────
    seccion("Identificación")
    j.nombre                  = pedir_texto("Nombre completo:")
    j.fecha_nacimiento        = pedir_texto("Fecha de nacimiento (YYYY-MM-DD):")
    j.edad                    = pedir_int("Edad:", 15, 45)
    j.pais_origen             = pedir_texto("País de origen:")
    j.ciudad_actual           = pedir_texto("Ciudad actual donde reside:")
    j.idioma                  = pedir_texto("Idioma principal:")
    j.experiencia_extranjero  = pedir_sino("¿Ha jugado o vivido en el extranjero antes?")
    j.valor_mercado           = pedir_texto("Valor de mercado Transfermarkt (ej: €150,000):")

    # ── Contrato ─────────────────────────────────────────────────
    seccion("Contrato")
    j.meses_contrato  = pedir_int("Meses restantes de contrato:", 0, 120)
    j.tiene_clausula  = pedir_sino("¿Tiene cláusula de rescisión?")
    if j.tiene_clausula:
        j.clausula_nivel = pedir_opcion(
            "Nivel de la cláusula:",
            ["accesible", "alta"],
            ["Accesible (factible de activar)", "Alta (difícil de activar)"],
        )

    # ── Club actual ───────────────────────────────────────────────
    seccion("Club actual")
    j.club_actual = pedir_texto("Nombre del club:")

    ligas = list(COEFICIENTES_LIGA.keys())
    etiquetas_ligas = [f"{l.replace('_', ' ').title()} (coef. {v})"
                       for l, v in COEFICIENTES_LIGA.items()]
    j.liga = pedir_opcion("Liga:", ligas, etiquetas_ligas)
    ok(f"Coeficiente de liga: {COEFICIENTES_LIGA[j.liga]}")

    j.posicion_tabla     = pedir_int("Posición actual en la tabla:", 1, 30)
    j.total_equipos_liga = pedir_int("Total de equipos en la liga:", 2, 30)
    j.tiene_copa         = pedir_sino("¿El club participa en copa nacional?")
    j.tiene_internacional= pedir_sino("¿El club participa en torneo internacional?")

    j.sistema_tactico_club = pedir_texto("Sistema táctico del club (ej: 4-3-3):")
    j.estilo_ofensivo      = pedir_texto("Estilo en fase ofensiva (descripción breve):")
    j.estilo_defensivo     = pedir_texto("Estilo en fase defensiva (descripción breve):")
    j.estilo_transicion    = pedir_texto("Estilo en fase de transición (descripción breve):")
    j.altitud_ciudad       = pedir_float("Altitud de la ciudad del club actual (metros):", 0.0)

    # ── Participación ─────────────────────────────────────────────
    seccion("Participación en cancha")
    j.minutos_jugados  = pedir_float("Minutos jugados en la temporada:", 0.0)
    j.minutos_posibles = pedir_float("Minutos posibles (partidos × 90):", 1.0)

    pct = (j.minutos_jugados / j.minutos_posibles) * 100
    ok(f"Porcentaje de minutos: {pct:.1f}%")

    j.posicion = pedir_opcion(
        "Posición del jugador:",
        POSICIONES,
        [p.replace("_", " ").title() for p in POSICIONES],
    )

    j.rol = pedir_opcion(
        "Rol en el equipo:",
        ["titular_indiscutible", "titular_con_competencia",
         "rotacion_habitual", "suplente", "sin_minutos"],
        ["Titular indiscutible", "Titular con competencia",
         "Rotación habitual", "Suplente", "Sin minutos relevantes"],
    )

    # ── Estadísticas brutas ───────────────────────────────────────
    seccion(f"Estadísticas brutas — {j.posicion.replace('_', ' ').title()}")
    print(f"  {chr(10)}  Ingresa los totales de temporada para cada métrica.\n")

    metricas = METRICAS_POR_POSICION.get(j.posicion, [])
    for label, key, _ in metricas:
        j.estadisticas[key] = pedir_float(f"{label}:", 0.0)

    # ── Físico y salud ─────────────────────────────────────────────
    seccion("Físico y salud")
    j.num_lesiones = pedir_int("Número de lesiones en los últimos 3 años:", 0, 20)

    if j.num_lesiones > 0:
        j.tipo_lesion = pedir_opcion(
            "Tipo de lesión predominante:",
            ["muscular", "ligamento", "fractura"],
            ["Muscular (distensión, desgarro)", "Ligamento (esguince, rotura LCA)",
             "Fractura ósea"],
        )
        j.semanas_baja_promedio = pedir_float("Promedio de semanas de baja por lesión:", 0.0)
    else:
        j.tipo_lesion           = "ninguna"
        j.semanas_baja_promedio = 0.0
        ok("Sin lesiones relevantes registradas.")

    # ── Zonas de presencia ─────────────────────────────────────────
    seccion("Zonas de presencia en el campo")
    j.zonas = pedir_zonas("zonas del jugador")
    ok(f"Zonas registradas: {j.zonas}")

    return j
