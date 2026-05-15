"""
MPSc — models/jugador.py
Clase Jugador: almacena todos los datos brutos del jugador evaluado.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Jugador:
    # Identificación
    nombre: str = ""
    fecha_nacimiento: str = ""          # "YYYY-MM-DD"
    edad: int = 0
    pais_origen: str = ""
    ciudad_actual: str = ""
    idioma: str = ""
    experiencia_extranjero: bool = False
    valor_mercado: str = ""             # Ej: "€150,000"

    # Contrato
    meses_contrato: int = 0
    tiene_clausula: bool = False
    clausula_nivel: str = ""            # "accesible" | "alta"

    # Club actual
    club_actual: str = ""
    liga: str = ""                      # clave de COEFICIENTES_LIGA
    posicion_tabla: int = 0
    total_equipos_liga: int = 0
    tiene_copa: bool = False
    tiene_internacional: bool = False
    sistema_tactico_club: str = ""
    estilo_ofensivo: str = ""
    estilo_defensivo: str = ""
    estilo_transicion: str = ""
    altitud_ciudad: float = 0.0         # metros

    # Participación
    minutos_jugados: float = 0.0
    minutos_posibles: float = 0.0
    posicion: str = ""                  # clave de POSICIONES
    rol: str = ""                       # "titular_indiscutible" | etc.

    # Estadísticas brutas (dict clave→valor)
    estadisticas: dict = field(default_factory=dict)

    # Físico y salud
    num_lesiones: int = 0
    tipo_lesion: str = ""               # "ninguna"|"muscular"|"ligamento"|"fractura"
    semanas_baja_promedio: float = 0.0

    # Zonas (lista de 5 zonas, índice 0 = mayor presencia)
    zonas: List[int] = field(default_factory=list)

    # Datos Sofascore del jugador (texto para parsear — estadísticas individuales)
    sofascore_jugador_raw: str = ""

    # Datos Sofascore del club actual (texto para parsear — contexto de equipo)
    stats_club_origen_raw: str = ""

    # Scores calculados (los llena el orquestador)
    scores: dict = field(default_factory=dict)
