"""
MPSc — models/club.py
Clase Club: almacena todos los datos del club destino.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Club:
    # Identificación
    nombre: str = ""
    ciudad: str = ""
    pais: str = ""
    idioma: str = ""
    altitud: float = 0.0                # metros

    # Situación deportiva
    liga: str = ""
    posicion_tabla: int = 0
    total_equipos_liga: int = 0
    victorias_recientes: int = 0
    empates_recientes: int = 0
    derrotas_recientes: int = 0
    tiene_copa: bool = False
    tiene_internacional: bool = False

    # Modelo de juego
    sistema_tactico: str = ""
    estilo_ofensivo: str = ""
    estilo_defensivo: str = ""
    estilo_transicion: str = ""

    # Necesidad técnico-táctica
    posicion_requerida: str = ""
    perfil_tactico: str = ""
    zonas_requeridas: List[int] = field(default_factory=list)

    # Plantilla
    jugadores_en_posicion: int = 0
    pct_minutos_proyectados: float = 0.0

    # Proyecto deportivo
    horizonte_anios: int = 0
    modo_competitivo: str = ""          # "resultados_inmediatos"|"consolidacion"|"desarrollo"

    # Umbrales estadísticos requeridos (clave→valor 1-10)
    umbrales_estadisticos: dict = field(default_factory=dict)

    # Datos Sofascore del club (texto para parsear — auto-thresholds)
    stats_aggregadas_raw: str = ""

    # Scores interpretativos (ingresados por el scout, 1-10)
    compat_tactica_ofensiva: float = 0.0
    compat_tactica_defensiva: float = 0.0
    compat_tactica_transicion: float = 0.0
    alineacion_edad_horizonte: float = 0.0
    alineacion_perfil_modo: float = 0.0
    proyeccion_continuidad: float = 0.0

    # Scores calculados
    scores: dict = field(default_factory=dict)
