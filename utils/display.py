"""
MPSc — utils/display.py
Funciones de presentación de resultados en consola.
"""
from models.resultado import Resultado
from utils.input_helper import pedir_opcion

R   = "\033[0m"
B   = "\033[1m"
G   = "\033[32m"
Y   = "\033[33m"
C   = "\033[36m"
M   = "\033[35m"
RD  = "\033[31m"
DIM = "\033[2m"
W   = "\033[37m"


def barra(valor: float, maximo: float = 100, ancho: int = 30) -> str:
    """Genera una barra de progreso ASCII."""
    lleno = int((valor / maximo) * ancho)
    vacio = ancho - lleno
    return f"[{'█' * lleno}{'░' * vacio}]"


def color_score(score: float) -> str:
    if score >= 85: return G
    if score >= 70: return Y
    if score >= 55: return Y
    if score >= 40: return M
    return RD


def mostrar_resultado(resultado: Resultado):
    ancho = 62

    print(f"\n{B}{C}{'═' * ancho}{R}")
    print(f"{B}{C}  RESULTADO — ÍNDICE DE COMPATIBILIDAD MPSc{R}")
    print(f"{B}{C}{'═' * ancho}{R}\n")

    print(f"  {B}Jugador:{R}       {resultado.nombre_jugador}")
    print(f"  {B}Club destino:{R}  {resultado.nombre_club}")
    print(f"  {B}Valor mercado:{R} {resultado.valor_mercado}")
    print(f"  {B}Perfil activo:{R} {resultado.perfil_evaluacion.replace('_', ' ').title()}")

    # ── Brecha de nivel ────────────────────────────────────────────
    niveles = {1: "1 — Baja", 2: "2 — Media", 3: "3 — Alta"}
    nivel_texto = niveles.get(resultado.nivel_brecha, str(resultado.nivel_brecha))
    print(f"\n  {B}Brecha de nivel:{R}     Nivel {nivel_texto}")
    print(f"  {B}Δcoef:{R}               {resultado.delta_coef}")
    if resultado.penalizacion_aplicada > 0:
        print(f"  {B}Penalización:{R}        {resultado.penalizacion_aplicada*100:.0f}% sobre score final")
    else:
        print(f"  {B}Penalización:{R}        Sin penalización")

    if resultado.confiabilidad_estadisticas < 1.0:
        conf_pct = resultado.confiabilidad_estadisticas * 100
        print(f"  {B}Confiabilidad stats:{R}  {conf_pct:.0f}%")
        if resultado.factor_contexto_global != 1.0:
            print(f"  {B}Factor contexto:{R}     {resultado.factor_contexto_global:.3f}")

    print(f"\n{B}{Y}  Compatibilidad por módulo{R}")
    print(f"  {DIM}{'─' * 58}{R}")

    nombres = {
        "entorno_competitivo": "Entorno competitivo",
        "perfil_jugador":      "Perfil del jugador",
        "estadisticas":        "Estadísticas",
        "fisico_salud":        "Físico y salud",
        "adaptacion":          "Adaptación",
        "zonas_presencia":     "Zonas de presencia",
        "modelo_juego":        "Modelo de juego",
        "viabilidad":          "Viabilidad contractual",
    }

    for key, compat in resultado.compatibilidades.items():
        sj = resultado.scores_jugador.get(key, "—")
        sc = resultado.scores_club.get(key, "—")
        pct = compat * 100
        col = color_score(pct)
        sj_str = f"{sj:.1f}" if isinstance(sj, float) else str(sj)
        sc_str = f"{sc:.1f}" if isinstance(sc, float) else str(sc)
        nombre = nombres.get(key, key)
        barra_str = barra(pct)
        print(f"  {nombre:<26} J:{sj_str:>4} C:{sc_str:>4}  {col}{pct:>5.1f}%{R}  {DIM}{barra_str}{R}")

    print(f"\n{B}{C}{'═' * ancho}{R}")

    perfiles = [
        ("Rendimiento inmediato",   resultado.score_rendimiento_inmediato),
        ("Potencial mediano plazo", resultado.score_potencial_mediano),
        ("Bajo riesgo de fracaso",  resultado.score_bajo_riesgo),
    ]

    for nombre, score in perfiles:
        col = color_score(score)
        marca = f"  {B}← ACTIVO{R}" if nombre.lower().replace(" ", "_") in resultado.perfil_evaluacion else ""
        bar = barra(score)
        print(f"  {nombre:<28} {col}{B}{score:>6.1f}%{R}  {DIM}{bar}{R}{marca}")

    print(f"\n{B}{C}{'═' * ancho}{R}")

    score_f = resultado.score_final
    col_f   = color_score(score_f)
    interp  = resultado.interpretacion()

    print(f"\n  {B}SCORE FINAL ({resultado.perfil_evaluacion.replace('_',' ').upper()}):{R}")
    print(f"\n  {col_f}{B}  {score_f:.1f}%  {barra(score_f, ancho=40)}{R}")
    print(f"\n  {col_f}{B}  {interp}{R}")

    abrir_reporte = pedir_opcion(
        "Abrir reporte visual en el navegador?",
        ["si", "no"],
        ["Si, abrir reporte grafico", "No, continuar"],
    )
    if abrir_reporte == "si":
        from utils.reporte_html import generar_reporte
        generar_reporte(resultado)

    print(f"\n{B}{C}{'═' * ancho}{R}\n")


def mostrar_detalle_estadisticas(detalle: dict):
    if not detalle:
        return
    print(f"\n{B}{Y}  Detalle estadísticas normalizadas{R}")
    print(f"  {DIM}{'─' * 58}{R}")
    print(f"  {'Métrica':<25} {'Valor':>8} {'μ':>8} {'σ':>6} {'Score':>6} {'Peso':>6}")
    print(f"  {DIM}{'─' * 58}{R}")
    for metrica, datos in detalle.items():
        print(f"  {metrica:<25} {datos['valor']:>8.3f} {datos['mu']:>8.3f} "
              f"{datos['sigma']:>6.3f} {datos['score']:>6.2f} {datos['peso']*100:>5.0f}%")
