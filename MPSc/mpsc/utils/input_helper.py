"""
MPSc — utils/input_helper.py
Funciones de entrada con validación, colores y display visual.
"""
import os
import sys

# ── Colores ANSI ────────────────────────────────────────────────────────────
R  = "\033[0m"        # Reset
B  = "\033[1m"        # Bold
G  = "\033[32m"       # Verde
Y  = "\033[33m"       # Amarillo
C  = "\033[36m"       # Cyan
M  = "\033[35m"       # Magenta
W  = "\033[37m"       # Blanco
RD = "\033[31m"       # Rojo
BG = "\033[42m"       # Fondo verde
DIM= "\033[2m"        # Dim

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def titulo(texto: str):
    ancho = 60
    print(f"\n{B}{C}{'═' * ancho}{R}")
    print(f"{B}{C}  {texto.upper()}{R}")
    print(f"{B}{C}{'═' * ancho}{R}\n")

def seccion(texto: str):
    print(f"\n{B}{Y}▶ {texto}{R}")
    print(f"{DIM}{'─' * 50}{R}")

def ok(texto: str):
    print(f"  {G}✓{R} {texto}")

def warn(texto: str):
    print(f"  {Y}⚠{R}  {texto}")

def error(texto: str):
    print(f"  {RD}✗{R} {texto}")

def pedir_float(mensaje: str, minimo: float = 0.0, maximo: float = None) -> float:
    while True:
        try:
            val = float(input(f"  {C}>{R} {mensaje} "))
            if maximo is not None and not (minimo <= val <= maximo):
                error(f"Valor debe estar entre {minimo} y {maximo}.")
                continue
            if val < minimo:
                error(f"Valor mínimo: {minimo}.")
                continue
            return val
        except ValueError:
            error("Ingresa un número válido.")

def pedir_int(mensaje: str, minimo: int = 0, maximo: int = None) -> int:
    while True:
        try:
            val = int(input(f"  {C}>{R} {mensaje} "))
            if maximo is not None and not (minimo <= val <= maximo):
                error(f"Valor debe estar entre {minimo} y {maximo}.")
                continue
            if val < minimo:
                error(f"Valor mínimo: {minimo}.")
                continue
            return val
        except ValueError:
            error("Ingresa un número entero válido.")

def pedir_texto(mensaje: str) -> str:
    val = input(f"  {C}>{R} {mensaje} ").strip()
    return val

def pedir_sino(mensaje: str) -> bool:
    while True:
        val = input(f"  {C}>{R} {mensaje} (s/n): ").strip().lower()
        if val in ("s", "si", "sí", "y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        error("Ingresa 's' o 'n'.")

def pedir_opcion(mensaje: str, opciones: list, etiquetas: list = None) -> str:
    etqs = etiquetas or opciones
    print(f"\n  {B}{mensaje}{R}")
    for i, (op, et) in enumerate(zip(opciones, etqs), 1):
        print(f"    {DIM}{i}.{R} {et}")
    while True:
        try:
            sel = int(input(f"  {C}>{R} Selección (1-{len(opciones)}): "))
            if 1 <= sel <= len(opciones):
                return opciones[sel - 1]
            error(f"Elige entre 1 y {len(opciones)}.")
        except ValueError:
            error("Ingresa un número.")

def pedir_score_interpretativo(concepto: str, descripcion: str) -> float:
    print(f"\n  {B}{concepto}{R}")
    print(f"  {DIM}{descripcion}{R}")
    print(f"  {DIM}Escala: 1=incompatible  5=parcial  10=perfectamente compatible{R}")
    return pedir_float("Score (1-10): ", 1.0, 10.0)

# ── Cancha visual ────────────────────────────────────────────────────────────

CAMPO = """
{titulo}

  ┌─────────────────────────────────────────────┐
  │         ╔═══════════════════╗               │
  │         ║    ARCO RIVAL     ║               │
  │         ╚═══════════════════╝               │
  ├───────────────┬──────────────┬──────────────┤
  │    {z1:^10}   │  {z2:^10}  │  {z3:^10}  │  ← ATAQUE
  │    Zona 1     │   Zona 2     │   Zona 3     │
  ├───────────────┼──────────────┼──────────────┤
  │    {z4:^10}   │  {z5:^10}  │  {z6:^10}  │  ← MED. ALTO
  │    Zona 4     │   Zona 5     │   Zona 6     │
  ├───────────────┼──────────────┼──────────────┤
  │    {z7:^10}   │  {z8:^10}  │  {z9:^10}  │  ← MED. BAJO
  │    Zona 7     │   Zona 8     │   Zona 9     │
  ├───────────────┼──────────────┼──────────────┤
  │   {z10:^10}   │  {z11:^10}  │  {z12:^10}  │  ← MED. DEF.
  │    Zona 10    │   Zona 11    │   Zona 12    │
  ├───────────────┼──────────────┼──────────────┤
  │   {z13:^10}   │  {z14:^10}  │  {z15:^10}  │  ← DEFENSA
  │    Zona 13    │   Zona 14    │   Zona 15    │
  ├───────────────┼──────────────┼──────────────┤
  │   {z16:^10}   │  {z17:^10}  │  {z18:^10}  │  ← ÁREA PROPIA
  │    Zona 16    │   Zona 17    │   Zona 18    │
  │         ╔═══════════════════╗               │
  │         ║   ARCO PROPIO     ║               │
  │         ╚═══════════════════╝               │
  └─────────────────────────────────────────────┘
    IZQUIERDA         CENTRO          DERECHA
"""

def mostrar_cancha(zonas_seleccionadas: list = None, titulo_texto: str = "ZONAS DEL CAMPO — MPSc"):
    """
    Muestra la cancha con las zonas resaltadas si se proporcionan.
    zonas_seleccionadas: lista de hasta 5 zonas, índice 0 = mayor presencia
    """
    colores_rango = [
        f"{B}\033[43m",   # 1° → fondo amarillo
        f"{B}\033[42m",   # 2° → fondo verde
        f"{B}\033[44m",   # 3° → fondo azul
        f"{B}\033[45m",   # 4° → fondo magenta
        f"{B}\033[46m",   # 5° → fondo cyan
    ]

    labels = {}
    if zonas_seleccionadas:
        for i, z in enumerate(zonas_seleccionadas[:5]):
            labels[z] = f"{colores_rango[i]} #{i+1} {R}"

    def zona_str(n: int) -> str:
        if n in labels:
            return labels[n]
        return "    "

    print(f"\n{B}{G}{'═' * 60}{R}")
    print(f"{B}{G}  {titulo_texto}{R}")
    print(f"{B}{G}{'═' * 60}{R}")

    print(CAMPO.format(
        titulo = "",
        z1=zona_str(1),   z2=zona_str(2),   z3=zona_str(3),
        z4=zona_str(4),   z5=zona_str(5),   z6=zona_str(6),
        z7=zona_str(7),   z8=zona_str(8),   z9=zona_str(9),
        z10=zona_str(10), z11=zona_str(11), z12=zona_str(12),
        z13=zona_str(13), z14=zona_str(14), z15=zona_str(15),
        z16=zona_str(16), z17=zona_str(17), z18=zona_str(18),
    ))

    if zonas_seleccionadas:
        print(f"  {B}Leyenda:{R}")
        colores_nombre = ["Amarillo(1°)","Verde(2°)","Azul(3°)","Magenta(4°)","Cyan(5°)"]
        for i, z in enumerate(zonas_seleccionadas[:5]):
            print(f"    {colores_nombre[i]} → Zona {z}")
        print()


def pedir_zonas(titulo_texto: str = "zonas del jugador") -> list:
    """Solicita las 5 zonas con visualización de la cancha."""
    mostrar_cancha(titulo_texto=f"SELECCIÓN DE {titulo_texto.upper()}")
    print(f"  {B}Ingresa las 5 zonas (1-18) de mayor a menor presencia:{R}\n")
    zonas = []
    for i in range(1, 6):
        while True:
            z = pedir_int(f"Zona {i} (1-18): ", 1, 18)
            if z in zonas:
                warn(f"La zona {z} ya fue seleccionada. Elige otra.")
            else:
                zonas.append(z)
                break
        mostrar_cancha(zonas, titulo_texto=f"SELECCIÓN DE {titulo_texto.upper()}")
    return zonas
