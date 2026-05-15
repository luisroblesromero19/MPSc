"""
MPSc — Modelo Predictivo de Scouting
config.py — Constantes, coeficientes y datos de referencia de liga
"""

# Minutos estándar de un partido
MIN_PROMEDIO_PARTIDO = 90

# Mapeo de nombres de métricas en formato Sofascore → claves internas
# Cada entrada: (nombre_sofascore, clave_interna, direccion)
# direccion: "directa" = percentil se traduce directo, "indirecta" = ajuste manual
MAPEO_METRICAS_SOFASCORE = {
    "balls recovered per game":     ("recuperaciones", "directa"),
    "interceptions per game":       ("intercepciones", "directa"),
    "accurate passes %":             ("pases_pct", "directa"),
    "duels won %":                   ("duelos_pct", "directa"),
    "aerial duels won %":            ("da_pct", "directa"),
    "goals scored per game":         ("goles_90", "directa"),
    "ball possession %":             ("pases_prog", "indirecta"),
    "acc. long balls %":             ("pases_largos_pct", "directa"),
    "succ. dribbles per game":       ("regates_ok_90", "directa"),
}

# Coeficientes de contribución posicional α
# Qué fracción de cada métrica del club corresponde a cada posición
# Formato: {metrica_club: {posicion: coeficiente}}
COEFICIENTES_CONTRIBUCION_ALFA = {
    "recuperaciones": {
        "portero": 0.3, "central": 0.8, "lateral": 0.7,
        "mediocampista_defensivo": 1.0, "mediocampista_central": 0.9,
        "extremo": 0.6, "delantero_centro": 0.4,
    },
    "intercepciones": {
        "portero": 0.2, "central": 0.9, "lateral": 0.8,
        "mediocampista_defensivo": 1.0, "mediocampista_central": 0.8,
        "extremo": 0.5, "delantero_centro": 0.3,
    },
    "pases_pct": {
        "portero": 0.6, "central": 0.9, "lateral": 0.9,
        "mediocampista_defensivo": 1.0, "mediocampista_central": 1.0,
        "extremo": 0.8, "delantero_centro": 0.7,
    },
    "da_pct": {
        "portero": 0.8, "central": 1.0, "lateral": 0.7,
        "mediocampista_defensivo": 0.8, "mediocampista_central": 0.6,
        "extremo": 0.5, "delantero_centro": 0.9,
    },
    "duelos_pct": {
        "portero": 0.4, "central": 0.9, "lateral": 0.8,
        "mediocampista_defensivo": 1.0, "mediocampista_central": 0.9,
        "extremo": 0.8, "delantero_centro": 0.7,
    },
    "goles_90": {
        "portero": 0.0, "central": 0.1, "lateral": 0.2,
        "mediocampista_defensivo": 0.1, "mediocampista_central": 0.3,
        "extremo": 0.8, "delantero_centro": 1.0,
    },
    "regates_ok_90": {
        "portero": 0.0, "central": 0.1, "lateral": 0.5,
        "mediocampista_defensivo": 0.2, "mediocampista_central": 0.4,
        "extremo": 1.0, "delantero_centro": 0.7,
    },
}

# Datos de referencia para clubes (μ y σ de estadísticas agregadas por liga)
# ADVERTENCIA: Estos son valores estimados. Para uso en producción,
# calibrar con datos reales de todos los clubes de cada liga.
REFERENCIA_CLUBES = {
    "liga_mx": {
        "recuperaciones":    {"mu": 85.0, "sigma": 15.0},
        "intercepciones":    {"mu": 35.0, "sigma": 8.0},
        "pases_pct":         {"mu": 75.0, "sigma": 8.0},
        "duelos_pct":        {"mu": 40.0, "sigma": 8.0},
        "da_pct":            {"mu": 45.0, "sigma": 8.0},
        "goles_90":          {"mu": 1.2,  "sigma": 0.4},
        "posesion_pct":      {"mu": 50.0, "sigma": 5.0},
        "pases_largos_pct":  {"mu": 55.0, "sigma": 8.0},
        "regates_ok_90":     {"mu": 8.0,  "sigma": 3.0},
    },
}

COEFICIENTES_LIGA = {
    "liga_mx":            1.00,
    "liga_expansion_mx":  0.75,
    "mls":                0.90,
    "liga_colombiana":    0.85,
    "liga_argentina":     0.95,
    "liga_chilena":       0.80,
    "liga_peruana":       0.75,
    "segunda_division_mx":0.60,
}

# Umbrales de brecha de coeficiente entre ligas
UMBRAL_BRECHA_MEDIA = 0.20
UMBRAL_BRECHA_ALTA  = 0.35

PENALIZACION_BRECHA = {
    "nivel_1": 0.00,
    "nivel_2": 0.08,
    "nivel_3": 0.15,
}

# Pesos por nivel de brecha × perfil de evaluación
# Nivel 1 — Brecha baja (Δcoef ≤ 0.20) — pesos originales sin cambio
PESOS_NIVEL_1 = {
    "rendimiento_inmediato": {
        "entorno_competitivo": 0.22,
        "perfil_jugador":      0.15,
        "estadisticas":        0.26,
        "fisico_salud":        0.12,
        "adaptacion":          0.10,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.10,
        "viabilidad":          0.05,
    },
    "potencial_mediano_plazo": {
        "entorno_competitivo": 0.12,
        "perfil_jugador":      0.20,
        "estadisticas":        0.16,
        "fisico_salud":        0.12,
        "adaptacion":          0.15,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.10,
        "viabilidad":          0.15,
    },
    "bajo_riesgo_fracaso": {
        "entorno_competitivo": 0.10,
        "perfil_jugador":      0.12,
        "estadisticas":        0.15,
        "fisico_salud":        0.30,
        "adaptacion":          0.20,
        "zonas_presencia":     0.08,
        "modelo_juego":        0.10,
        "viabilidad":          0.05,
    },
}

# Nivel 2 — Brecha media (0.20 < Δcoef ≤ 0.35)
# estadísticas −8%, modelo de juego +5%, entorno +3%
PESOS_NIVEL_2 = {
    "rendimiento_inmediato": {
        "entorno_competitivo": 0.25,
        "perfil_jugador":      0.15,
        "estadisticas":        0.18,
        "fisico_salud":        0.12,
        "adaptacion":          0.10,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.15,
        "viabilidad":          0.05,
    },
    "potencial_mediano_plazo": {
        "entorno_competitivo": 0.15,
        "perfil_jugador":      0.20,
        "estadisticas":        0.08,
        "fisico_salud":        0.12,
        "adaptacion":          0.15,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.15,
        "viabilidad":          0.15,
    },
    "bajo_riesgo_fracaso": {
        "entorno_competitivo": 0.13,
        "perfil_jugador":      0.12,
        "estadisticas":        0.07,
        "fisico_salud":        0.30,
        "adaptacion":          0.20,
        "zonas_presencia":     0.08,
        "modelo_juego":        0.15,
        "viabilidad":          0.05,
    },
}

# Nivel 3 — Brecha alta (Δcoef > 0.35)
# estadísticas −14%, modelo de juego +8%, entorno +6%
PESOS_NIVEL_3 = {
    "rendimiento_inmediato": {
        "entorno_competitivo": 0.28,
        "perfil_jugador":      0.15,
        "estadisticas":        0.12,
        "fisico_salud":        0.12,
        "adaptacion":          0.10,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.18,
        "viabilidad":          0.05,
    },
    "potencial_mediano_plazo": {
        "entorno_competitivo": 0.18,
        "perfil_jugador":      0.20,
        "estadisticas":        0.02,
        "fisico_salud":        0.12,
        "adaptacion":          0.15,
        "zonas_presencia":     0.10,
        "modelo_juego":        0.18,
        "viabilidad":          0.15,
    },
    "bajo_riesgo_fracaso": {
        "entorno_competitivo": 0.16,
        "perfil_jugador":      0.12,
        "estadisticas":        0.01,
        "fisico_salud":        0.30,
        "adaptacion":          0.20,
        "zonas_presencia":     0.08,
        "modelo_juego":        0.18,
        "viabilidad":          0.05,
    },
}

PESOS = PESOS_NIVEL_1  # alias para compatibilidad hacia atrás

# Promedios (mu) y desviaciones estándar (sigma) por posición y liga
# Fuente: valores estimados basados en el ejemplo MPSc v1.0
# Para actualizar con datos reales usar utils/calibrador.py con datos de FBref

ESTADISTICAS_REFERENCIA = {
    "liga_mx": {
        "portero": {
            "salvadas_90":      {"mu": 3.20, "sigma": 0.80},
            "gc_90":            {"mu": 1.20, "sigma": 0.35},
            "save_pct":         {"mu": 72.0, "sigma": 8.0},
            "salidas_90":       {"mu": 1.80, "sigma": 0.60},
            "pases_pct":        {"mu": 62.0, "sigma": 10.0},
            "da_pct":           {"mu": 55.0, "sigma": 12.0},
        },
        "central": {
            "despejes_90":      {"mu": 5.50, "sigma": 1.80},
            "intercepciones_90":{"mu": 1.80, "sigma": 0.65},
            "entradas_90":      {"mu": 2.20, "sigma": 0.80},
            "pases_prog_90":    {"mu": 3.20, "sigma": 1.10},
            "da_pct":           {"mu": 58.0, "sigma": 12.0},
            "dt_pct":           {"mu": 55.0, "sigma": 10.0},
            "pases_pct":        {"mu": 78.0, "sigma": 7.0},
            "pases_largos_pct": {"mu": 62.0, "sigma": 10.0},
        },
        "lateral": {
            "centros_90":       {"mu": 2.80, "sigma": 1.00},
            "centros_pct":      {"mu": 28.0, "sigma": 8.0},
            "pases_prog_90":    {"mu": 4.20, "sigma": 1.30},
            "carreras_prog_90": {"mu": 3.50, "sigma": 1.20},
            "intercepciones_90":{"mu": 1.50, "sigma": 0.55},
            "entradas_90":      {"mu": 2.00, "sigma": 0.70},
            "do_pct":           {"mu": 42.0, "sigma": 10.0},
            "dd_pct":           {"mu": 60.0, "sigma": 10.0},
            "pases_pct":        {"mu": 76.0, "sigma": 7.0},
        },
        "mediocampista_defensivo": {
            "intercepciones_90": {"mu": 2.10, "sigma": 0.70},
            "entradas_90":       {"mu": 2.80, "sigma": 0.90},
            "presiones_90":      {"mu": 8.50, "sigma": 2.50},
            "presiones_pct":     {"mu": 28.0, "sigma": 7.0},
            "pases_prog_90":     {"mu": 4.80, "sigma": 1.50},
            "recuperaciones_90": {"mu": 5.20, "sigma": 1.60},
            "da_pct":            {"mu": 52.0, "sigma": 11.0},
            "pases_pct":         {"mu": 82.0, "sigma": 6.0},
        },
        "mediocampista_central": {
            "pases_prog_90":    {"mu": 5.50, "sigma": 1.80},
            "pases_clave_90":   {"mu": 1.20, "sigma": 0.45},
            "carreras_prog_90": {"mu": 3.80, "sigma": 1.20},
            "llegadas_area_90": {"mu": 1.50, "sigma": 0.60},
            "recuperaciones_90":{"mu": 4.20, "sigma": 1.30},
            "tiros_90":         {"mu": 1.10, "sigma": 0.40},
            "pases_pct":        {"mu": 80.0, "sigma": 6.0},
            "xg_90":            {"mu": 0.08, "sigma": 0.04},
            "xa_90":            {"mu": 0.10, "sigma": 0.05},
        },
        "extremo": {
            "tiros_90":         {"mu": 1.80, "sigma": 0.65},
            "tiros_puerta_90":  {"mu": 0.80, "sigma": 0.30},
            "regates_pct":      {"mu": 48.0, "sigma": 12.0},
            "pases_clave_90":   {"mu": 1.10, "sigma": 0.40},
            "centros_pct":      {"mu": 26.0, "sigma": 8.0},
            "carreras_prog_90": {"mu": 4.20, "sigma": 1.40},
            "pases_pct":        {"mu": 72.0, "sigma": 8.0},
            "xg_90":            {"mu": 0.14, "sigma": 0.06},
            "xa_90":            {"mu": 0.12, "sigma": 0.05},
        },
        "delantero_centro": {
            "goles_90":         {"mu": 0.35, "sigma": 0.12},
            "tiros_90":         {"mu": 2.10, "sigma": 0.65},
            "tiros_puerta_90":  {"mu": 1.20, "sigma": 0.38},
            "toques_area_90":   {"mu": 4.80, "sigma": 1.20},
            "da_pct":           {"mu": 48.0, "sigma": 12.0},
            "faltas_rec_90":    {"mu": 1.80, "sigma": 0.55},
            "pases_pct":        {"mu": 68.0, "sigma": 8.0},
            "xg_90":            {"mu": 0.32, "sigma": 0.12},
            "conversion_pct":   {"mu": 38.0, "sigma": 10.0},
        },
    },
    "liga_expansion_mx": {
        "portero": {
            "salvadas_90":      {"mu": 3.50, "sigma": 0.90},
            "gc_90":            {"mu": 1.40, "sigma": 0.40},
            "save_pct":         {"mu": 68.0, "sigma": 9.0},
            "salidas_90":       {"mu": 1.60, "sigma": 0.55},
            "pases_pct":        {"mu": 58.0, "sigma": 11.0},
            "da_pct":           {"mu": 52.0, "sigma": 13.0},
        },
        "central": {
            "despejes_90":      {"mu": 6.20, "sigma": 2.00},
            "intercepciones_90":{"mu": 1.60, "sigma": 0.60},
            "entradas_90":      {"mu": 2.50, "sigma": 0.90},
            "pases_prog_90":    {"mu": 2.60, "sigma": 0.95},
            "da_pct":           {"mu": 54.0, "sigma": 13.0},
            "dt_pct":           {"mu": 51.0, "sigma": 11.0},
            "pases_pct":        {"mu": 72.0, "sigma": 8.0},
            "pases_largos_pct": {"mu": 56.0, "sigma": 11.0},
        },
        "lateral": {
            "centros_90":       {"mu": 3.10, "sigma": 1.10},
            "centros_pct":      {"mu": 24.0, "sigma": 8.0},
            "pases_prog_90":    {"mu": 3.60, "sigma": 1.20},
            "carreras_prog_90": {"mu": 3.10, "sigma": 1.10},
            "intercepciones_90":{"mu": 1.30, "sigma": 0.50},
            "entradas_90":      {"mu": 2.20, "sigma": 0.75},
            "do_pct":           {"mu": 38.0, "sigma": 11.0},
            "dd_pct":           {"mu": 56.0, "sigma": 11.0},
            "pases_pct":        {"mu": 70.0, "sigma": 8.0},
        },
        "mediocampista_defensivo": {
            "intercepciones_90": {"mu": 2.30, "sigma": 0.80},
            "entradas_90":       {"mu": 3.10, "sigma": 1.00},
            "presiones_90":      {"mu": 9.20, "sigma": 2.80},
            "presiones_pct":     {"mu": 25.0, "sigma": 7.0},
            "pases_prog_90":     {"mu": 4.00, "sigma": 1.30},
            "recuperaciones_90": {"mu": 5.80, "sigma": 1.80},
            "da_pct":            {"mu": 48.0, "sigma": 12.0},
            "pases_pct":         {"mu": 76.0, "sigma": 7.0},
        },
        "mediocampista_central": {
            "pases_prog_90":    {"mu": 4.60, "sigma": 1.60},
            "pases_clave_90":   {"mu": 1.00, "sigma": 0.40},
            "carreras_prog_90": {"mu": 3.20, "sigma": 1.10},
            "llegadas_area_90": {"mu": 1.20, "sigma": 0.55},
            "recuperaciones_90":{"mu": 4.60, "sigma": 1.40},
            "tiros_90":         {"mu": 0.90, "sigma": 0.35},
            "pases_pct":        {"mu": 74.0, "sigma": 7.0},
            "xg_90":            {"mu": 0.06, "sigma": 0.03},
            "xa_90":            {"mu": 0.08, "sigma": 0.04},
        },
        "extremo": {
            "tiros_90":         {"mu": 2.00, "sigma": 0.70},
            "tiros_puerta_90":  {"mu": 0.90, "sigma": 0.32},
            "regates_pct":      {"mu": 44.0, "sigma": 13.0},
            "pases_clave_90":   {"mu": 0.90, "sigma": 0.38},
            "centros_pct":      {"mu": 22.0, "sigma": 8.0},
            "carreras_prog_90": {"mu": 3.80, "sigma": 1.30},
            "pases_pct":        {"mu": 66.0, "sigma": 9.0},
            "xg_90":            {"mu": 0.12, "sigma": 0.06},
            "xa_90":            {"mu": 0.10, "sigma": 0.05},
        },
        "delantero_centro": {
            "goles_90":         {"mu": 0.32, "sigma": 0.14},
            "tiros_90":         {"mu": 2.10, "sigma": 0.65},
            "tiros_puerta_90":  {"mu": 1.20, "sigma": 0.38},
            "toques_area_90":   {"mu": 4.80, "sigma": 1.20},
            "da_pct":           {"mu": 48.0, "sigma": 12.0},
            "faltas_rec_90":    {"mu": 1.80, "sigma": 0.55},
            "pases_pct":        {"mu": 68.0, "sigma": 8.0},
            "xg_90":            {"mu": 0.28, "sigma": 0.12},
            "conversion_pct":   {"mu": 35.0, "sigma": 11.0},
        },
    },
    "liga_argentina": {
        "delantero_centro": {
            "goles_90":         {"mu": 0.38, "sigma": 0.13},
            "tiros_90":         {"mu": 2.30, "sigma": 0.70},
            "tiros_puerta_90":  {"mu": 1.30, "sigma": 0.40},
            "toques_area_90":   {"mu": 5.10, "sigma": 1.30},
            "da_pct":           {"mu": 50.0, "sigma": 12.0},
            "faltas_rec_90":    {"mu": 2.00, "sigma": 0.60},
            "pases_pct":        {"mu": 70.0, "sigma": 8.0},
            "xg_90":            {"mu": 0.34, "sigma": 0.13},
            "conversion_pct":   {"mu": 40.0, "sigma": 10.0},
        },
        "central": {
            "despejes_90":      {"mu": 5.80, "sigma": 1.90},
            "intercepciones_90":{"mu": 1.90, "sigma": 0.68},
            "entradas_90":      {"mu": 2.40, "sigma": 0.85},
            "pases_prog_90":    {"mu": 3.40, "sigma": 1.15},
            "da_pct":           {"mu": 60.0, "sigma": 12.0},
            "dt_pct":           {"mu": 57.0, "sigma": 10.0},
            "pases_pct":        {"mu": 80.0, "sigma": 7.0},
            "pases_largos_pct": {"mu": 64.0, "sigma": 10.0},
        },
    },
    "mls": {
        "extremo": {
            "tiros_90":         {"mu": 1.90, "sigma": 0.68},
            "tiros_puerta_90":  {"mu": 0.85, "sigma": 0.31},
            "regates_pct":      {"mu": 50.0, "sigma": 12.0},
            "pases_clave_90":   {"mu": 1.15, "sigma": 0.42},
            "centros_pct":      {"mu": 28.0, "sigma": 8.0},
            "carreras_prog_90": {"mu": 4.40, "sigma": 1.45},
            "pases_pct":        {"mu": 74.0, "sigma": 8.0},
            "xg_90":            {"mu": 0.15, "sigma": 0.06},
            "xa_90":            {"mu": 0.13, "sigma": 0.05},
        },
    },
    "liga_colombiana": {
        "mediocampista_central": {
            "pases_prog_90":    {"mu": 4.80, "sigma": 1.65},
            "pases_clave_90":   {"mu": 1.05, "sigma": 0.42},
            "carreras_prog_90": {"mu": 3.40, "sigma": 1.15},
            "llegadas_area_90": {"mu": 1.30, "sigma": 0.57},
            "recuperaciones_90":{"mu": 4.40, "sigma": 1.35},
            "tiros_90":         {"mu": 0.95, "sigma": 0.37},
            "pases_pct":        {"mu": 76.0, "sigma": 7.0},
            "xg_90":            {"mu": 0.07, "sigma": 0.03},
            "xa_90":            {"mu": 0.09, "sigma": 0.04},
        },
    },
}

ZONAS_DESCRIPCION = {
    1:  "Izq. ataque",    2:  "Centro ataque",   3:  "Der. ataque",
    4:  "Med. alto izq.", 5:  "Med. alto centro", 6:  "Med. alto der.",
    7:  "Med. bajo izq.", 8:  "Med. bajo centro", 9:  "Med. bajo der.",
    10: "Med. def. izq.", 11: "Med. def. centro", 12: "Med. def. der.",
    13: "Def. izq.",      14: "Def. centro",      15: "Def. der.",
    16: "Área prop. izq.",17: "Área prop. centro",18: "Área prop. der.",
}

POSICIONES = [
    "portero",
    "central",
    "lateral",
    "mediocampista_defensivo",
    "mediocampista_central",
    "extremo",
    "delantero_centro",
]

METRICAS_POR_POSICION = {
    "portero": [
        ("Salvadas totales",           "salvadas",      "salvadas_90"),
        ("Goles encajados totales",    "gc",            "gc_90"),
        ("Tiros al arco recibidos",    "tiros_rec",     None),
        ("Porterías a cero",           "porterias_0",   None),
        ("Salidas del área totales",   "salidas",       "salidas_90"),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
        ("Duelos aéreos ganados",      "da_ganados",    None),
        ("Duelos aéreos disputados",   "da_disputados", None),
    ],
    "central": [
        ("Despejes totales",           "despejes",      "despejes_90"),
        ("Intercepciones totales",     "intercepciones","intercepciones_90"),
        ("Entradas/tackles totales",   "entradas",      "entradas_90"),
        ("Pases progresivos totales",  "pases_prog",    "pases_prog_90"),
        ("Duelos aéreos ganados",      "da_ganados",    None),
        ("Duelos aéreos disputados",   "da_disputados", None),
        ("Duelos terrestres ganados",  "dt_ganados",    None),
        ("Duelos terrestres disp.",    "dt_disputados", None),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
        ("Pases largos completados",   "pases_l_comp",  None),
        ("Pases largos intentados",    "pases_l_int",   None),
    ],
    "lateral": [
        ("Centros totales",            "centros",       None),
        ("Centros completados",        "centros_comp",  None),
        ("Pases progresivos totales",  "pases_prog",    "pases_prog_90"),
        ("Carreras progresivas tot.",  "carreras_prog", "carreras_prog_90"),
        ("Intercepciones totales",     "intercepciones","intercepciones_90"),
        ("Entradas/tackles totales",   "entradas",      "entradas_90"),
        ("Duelos ofensivos ganados",   "do_ganados",    None),
        ("Duelos ofensivos disp.",     "do_disputados", None),
        ("Duelos defensivos ganados",  "dd_ganados",    None),
        ("Duelos defensivos disp.",    "dd_disputados", None),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
    ],
    "mediocampista_defensivo": [
        ("Intercepciones totales",     "intercepciones","intercepciones_90"),
        ("Entradas/tackles totales",   "entradas",      "entradas_90"),
        ("Presiones totales",          "presiones",     "presiones_90"),
        ("Presiones exitosas",         "presiones_ok",  None),
        ("Pases progresivos totales",  "pases_prog",    "pases_prog_90"),
        ("Recuperaciones totales",     "recuperaciones","recuperaciones_90"),
        ("Duelos aéreos ganados",      "da_ganados",    None),
        ("Duelos aéreos disputados",   "da_disputados", None),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
    ],
    "mediocampista_central": [
        ("Pases progresivos totales",  "pases_prog",    "pases_prog_90"),
        ("Pases clave totales",        "pases_clave",   "pases_clave_90"),
        ("Carreras progresivas tot.",  "carreras_prog", "carreras_prog_90"),
        ("Llegadas al área totales",   "llegadas_area", "llegadas_area_90"),
        ("Recuperaciones totales",     "recuperaciones","recuperaciones_90"),
        ("Tiros totales",              "tiros",         "tiros_90"),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
    ],
    "extremo": [
        ("Tiros totales",              "tiros",         "tiros_90"),
        ("Tiros a puerta totales",     "tiros_puerta",  "tiros_puerta_90"),
        ("Regates intentados",         "regates_int",   None),
        ("Regates exitosos",           "regates_ok",    None),
        ("Pases clave totales",        "pases_clave",   "pases_clave_90"),
        ("Centros totales",            "centros",       None),
        ("Centros completados",        "centros_comp",  None),
        ("Carreras progresivas tot.",  "carreras_prog", "carreras_prog_90"),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
    ],
    "delantero_centro": [
        ("Goles totales",              "goles",         "goles_90"),
        ("Tiros totales",              "tiros",         "tiros_90"),
        ("Tiros a puerta totales",     "tiros_puerta",  "tiros_puerta_90"),
        ("Toques en área rival tot.",  "toques_area",   "toques_area_90"),
        ("Duelos aéreos ganados",      "da_ganados",    None),
        ("Duelos aéreos disputados",   "da_disputados", None),
        ("Faltas recibidas totales",   "faltas_rec",    "faltas_rec_90"),
        ("Pases completados",          "pases_comp",    None),
        ("Pases intentados",           "pases_int",     None),
    ],
}

# Mapeo de métricas de jugador en formato Sofascore → claves internas del sistema
# Formato: "(keyword sofascore)": ("clave_interna", "tipo_conversion")
#   "total": valor directo (goles, salvadas, etc.)
#   "per_game": valor por partido → se multiplica por partidos jugados
#   "percentage": porcentaje pre-calculado
MAPEO_SOFASCORE_JUGADOR = {
    "goals":                     ("goles", "total"),
    "goles":                     ("goles", "total"),
    "assists":                   ("asistencias", "total"),
    "asistencias":               ("asistencias", "total"),
    "saves":                     ("salvadas", "total"),
    "salvadas":                  ("salvadas", "total"),
    "goals conceded":            ("gc", "total"),
    "goles encajados":           ("gc", "total"),
    "shots against":             ("tiros_rec", "total"),
    "tiros al arco recibidos":   ("tiros_rec", "total"),
    "clean sheets":              ("porterias_0", "total"),
    "porterias a cero":          ("porterias_0", "total"),
    "shots per game":            ("tiros", "per_game"),
    "shots on target per game":  ("tiros_puerta", "per_game"),
    "passes per game":           ("pases_comp", "per_game"),
    "tackles per game":          ("entradas", "per_game"),
    "entradas por partido":      ("entradas", "per_game"),
    "interceptions per game":    ("intercepciones", "per_game"),
    "fouls per game":            ("faltas_rec", "per_game"),
    "faltas por partido":        ("faltas_rec", "per_game"),
    "key passes per game":       ("pases_clave", "per_game"),
    "crosses per game":          ("centros", "per_game"),
    "centros por partido":       ("centros", "per_game"),
    "dribbles per game":         ("regates_int", "per_game"),
    "regates por partido":       ("regates_int", "per_game"),
    "clearances per game":       ("despejes", "per_game"),
    "despejes por partido":      ("despejes", "per_game"),
    "aerial duels won per game": ("da_ganados", "per_game"),
    "aerial duels lost per game":("da_perdidos", "per_game"),
    "duels won per game":        ("dt_ganados", "per_game"),
    "duels lost per game":       ("dt_perdidos", "per_game"),
    "recoveries per game":       ("recuperaciones", "per_game"),
    "recuperaciones por partido":("recuperaciones", "per_game"),
    "progressive passes per game":("pases_prog", "per_game"),
    "progressive runs per game": ("carreras_prog", "per_game"),
    "touches in box per game":   ("toques_area", "per_game"),
    "toques en area por partido":("toques_area", "per_game"),
    "pass accuracy":             ("pases_pct", "percentage"),
    "precisión de pases":        ("pases_pct", "percentage"),
    "duels won %":               ("dt_pct", "percentage"),
    "aerial duels won %":        ("da_pct", "percentage"),
    "tackles won %":             ("dd_pct", "percentage"),
    "dribble success %":         ("regates_pct", "percentage"),
    "cross accuracy %":          ("centros_pct", "percentage"),
    "shot conversion %":         ("conversion_pct", "percentage"),
    "press success %":           ("presiones_pct", "percentage"),
    "saves %":                   ("save_pct", "percentage"),
    "presiones exitosas %":      ("presiones_pct", "percentage"),
}

PESOS_ESTADISTICAS = {
    "portero": {
        "save_pct":      0.30,
        "gc_90":         0.25,
        "salvadas_90":   0.20,
        "salidas_90":    0.10,
        "pases_pct":     0.10,
        "da_pct":        0.05,
    },
    "central": {
        "da_pct":           0.20,
        "dt_pct":           0.20,
        "despejes_90":      0.15,
        "intercepciones_90":0.15,
        "pases_prog_90":    0.15,
        "pases_pct":        0.10,
        "pases_largos_pct": 0.05,
    },
    "lateral": {
        "centros_pct":      0.20,
        "pases_prog_90":    0.20,
        "carreras_prog_90": 0.15,
        "do_pct":           0.15,
        "dd_pct":           0.15,
        "intercepciones_90":0.10,
        "pases_pct":        0.05,
    },
    "mediocampista_defensivo": {
        "recuperaciones_90": 0.25,
        "intercepciones_90": 0.20,
        "entradas_90":       0.20,
        "presiones_pct":     0.15,
        "pases_prog_90":     0.15,
        "pases_pct":         0.05,
    },
    "mediocampista_central": {
        "pases_clave_90":   0.20,
        "pases_prog_90":    0.20,
        "xg_90":            0.15,
        "xa_90":            0.15,
        "carreras_prog_90": 0.15,
        "recuperaciones_90":0.10,
        "pases_pct":        0.05,
    },
    "extremo": {
        "xg_90":            0.20,
        "xa_90":            0.15,
        "regates_pct":      0.20,
        "tiros_90":         0.15,
        "carreras_prog_90": 0.15,
        "pases_clave_90":   0.10,
        "pases_pct":        0.05,
    },
    "delantero_centro": {
        "goles_90":         0.25,
        "xg_90":            0.20,
        "tiros_puerta_90":  0.15,
        "conversion_pct":   0.15,
        "toques_area_90":   0.10,
        "da_pct":           0.10,
        "pases_pct":        0.05,
    },
}
