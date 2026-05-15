"""
MPSc — main.py
Modelo Predictivo de Scouting — Punto de entrada principal.

Uso:
    python main.py
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PESOS
from calculadora import Calculadora
from utils.input_helper import (
    limpiar, titulo, seccion, ok, warn, pedir_opcion,
)
from utils.formulario_jugador import capturar_jugador
from utils.formulario_club import capturar_club
from utils.display import mostrar_resultado, mostrar_detalle_estadisticas


BANNER = r"""
  __  __ ____  ____
 |  \/  |  _ \/ ___|  c
 | |\/| | |_) \___ \  Modelo Predictivo de Scouting
 | |  | |  __/ ___) |
 |_|  |_|_|   |____/  v1.0
"""

R  = "\033[0m"
B  = "\033[1m"
G  = "\033[32m"
C  = "\033[36m"
Y  = "\033[33m"
DIM= "\033[2m"


def menu_principal() -> str:
    print(f"\n{B}{C}  ¿Qué deseas hacer?{R}\n")
    opciones = [
        "nueva_evaluacion",
        "salir",
    ]
    etiquetas = [
        "Nueva evaluación de compatibilidad",
        "Salir",
    ]
    return pedir_opcion("Opción:", opciones, etiquetas)


def seleccionar_perfil() -> str:
    perfiles = list(PESOS.keys())
    etiquetas = [
        "Rendimiento inmediato  — El jugador debe aportar desde ya",
        "Potencial mediano plazo — Apuesta a futuro, jugador en desarrollo",
        "Bajo riesgo de fracaso  — Prioridad en seguridad y adaptación",
    ]
    return pedir_opcion("Selecciona el perfil de evaluación:", perfiles, etiquetas)


def ejecutar_evaluacion():
    calc = Calculadora()

    # ── Capturar datos ──────────────────────────────────────────
    jugador = capturar_jugador()
    club    = capturar_club()

    # ── Seleccionar perfil ──────────────────────────────────────
    seccion("Perfil de evaluación")
    perfil = seleccionar_perfil()
    ok(f"Perfil activo: {perfil.replace('_', ' ').title()}")

    # ── Calcular ────────────────────────────────────────────────
    print(f"\n  {DIM}Calculando compatibilidad...{R}")
    resultado = calc.calcular(jugador, club, perfil)

    # ── Mostrar resultado ───────────────────────────────────────
    mostrar_resultado(resultado)

    # Detalle estadístico opcional
    detalle = jugador.scores.get("detalle_estadisticas", {})
    if detalle:
        ver_detalle = pedir_opcion(
            "¿Ver detalle de estadísticas normalizadas?",
            ["si", "no"],
            ["Sí, mostrar detalle", "No, continuar"],
        )
        if ver_detalle == "si":
            mostrar_detalle_estadisticas(detalle)

    input(f"\n  {DIM}Presiona Enter para continuar...{R}")


def main():
    limpiar()
    print(f"{B}{C}{BANNER}{R}")
    print(f"  {DIM}Sistema de evaluación de compatibilidad jugador ↔ club{R}\n")

    while True:
        accion = menu_principal()

        if accion == "nueva_evaluacion":
            ejecutar_evaluacion()
            limpiar()
            print(f"{B}{C}{BANNER}{R}")

        elif accion == "salir":
            print(f"\n  {G}Hasta pronto.{R}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
