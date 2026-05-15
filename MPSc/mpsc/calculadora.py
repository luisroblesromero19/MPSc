"""
MPSc — calculadora.py
Orquestador: coordina todos los módulos y produce el Resultado final.
"""
from config import (
    COEFICIENTES_LIGA, PESOS_NIVEL_1, PESOS_NIVEL_2, PESOS_NIVEL_3,
    PENALIZACION_BRECHA, UMBRAL_BRECHA_MEDIA, UMBRAL_BRECHA_ALTA,
)
from models.jugador import Jugador
from models.club import Club
from models.resultado import Resultado
from modules.entorno import ModuloEntorno
from modules.perfil import ModuloPerfil
from modules.estadisticas import ModuloEstadisticas
from modules.fisico import ModuloFisico
from modules.adaptacion import ModuloAdaptacion
from modules.zonas import ModuloZonas
from modules.tactico import ModuloModeloJuego, ModuloProyecto, ModuloActualidadClub
from modules.viabilidad import ModuloViabilidad
from modules.contexto_equipo import (
    parsear_sofascore, calcular_umbrales_auto,
    calcular_factor_contexto, aplicar_correccion_stats,
)
from utils.normalizacion import compatibilidad_modulo


class Calculadora:

    MAPA_NIVELES = {1: PESOS_NIVEL_1, 2: PESOS_NIVEL_2, 3: PESOS_NIVEL_3}

    def __init__(self):
        self.entorno     = ModuloEntorno()
        self.perfil      = ModuloPerfil()
        self.estadisticas= ModuloEstadisticas()
        self.fisico      = ModuloFisico()
        self.adaptacion  = ModuloAdaptacion()
        self.zonas       = ModuloZonas()
        self.modelo_juego= ModuloModeloJuego()
        self.proyecto    = ModuloProyecto()
        self.actualidad  = ModuloActualidadClub()
        self.viabilidad  = ModuloViabilidad()

    def _determinar_nivel_brecha(self, coef_origen: float, coef_destino: float) -> int:
        delta = abs(coef_destino - coef_origen)
        if delta <= UMBRAL_BRECHA_MEDIA:
            return 1
        if delta <= UMBRAL_BRECHA_ALTA:
            return 2
        return 3

    def calcular(self, jugador: Jugador, club: Club,
                 perfil_evaluacion: str = "rendimiento_inmediato") -> Resultado:

        coef_j = COEFICIENTES_LIGA.get(jugador.liga, 0.70)
        coef_c = COEFICIENTES_LIGA.get(club.liga, 0.70)

        nivel_brecha = self._determinar_nivel_brecha(coef_j, coef_c)
        delta_coef = round(abs(coef_c - coef_j), 2)
        pesos_activos = self.MAPA_NIVELES[nivel_brecha]
        penalizacion = PENALIZACION_BRECHA[f"nivel_{nivel_brecha}"]

        filtro_duro = (jugador.posicion.lower().strip() ==
                       club.posicion_requerida.lower().strip())

        # ── Scores jugador ──────────────────────────────────────
        sj = {}

        sj["entorno_competitivo"] = self.entorno.calcular(
            jugador.liga, jugador.posicion_tabla,
            jugador.total_equipos_liga,
            jugador.tiene_copa, jugador.tiene_internacional,
        )

        sj["perfil_jugador"] = self.perfil.calcular(
            jugador.edad, jugador.rol,
            jugador.minutos_jugados, jugador.minutos_posibles,
            filtro_duro,
        )

        # ── Estadísticas base ────────────────────────────────────
        sj["estadisticas"], jugador.scores["detalle_estadisticas"] = \
            self.estadisticas.calcular(
                jugador.posicion, jugador.liga, coef_j,
                jugador.estadisticas, jugador.minutos_jugados,
            )

        # ── Corrección por contexto de equipo (Sofascore) ────────
        factor_contexto_global = 1.0
        confiabilidad_est = 1.0
        detalle_est = jugador.scores.get("detalle_estadisticas", {})
        if jugador.stats_club_origen_raw and detalle_est:
            datos_origen = parsear_sofascore(jugador.stats_club_origen_raw)
            if datos_origen:
                fg, corr, conf = calcular_factor_contexto(
                    datos_origen, detalle_est,
                    jugador.liga, jugador.posicion,
                )
                sj["estadisticas"] = aplicar_correccion_stats(sj["estadisticas"], corr)
                factor_contexto_global = fg
                confiabilidad_est = conf

        sj["fisico_salud"] = self.fisico.calcular(
            jugador.num_lesiones, jugador.tipo_lesion,
            jugador.semanas_baja_promedio,
            jugador.minutos_jugados, jugador.minutos_posibles,
            jugador.altitud_ciudad, club.altitud,
        )

        sj["adaptacion"] = self.adaptacion.calcular(
            jugador.idioma, club.idioma,
            jugador.experiencia_extranjero,
            jugador.pais_origen, club.pais,
            jugador.ciudad_actual, club.ciudad,
            jugador.altitud_ciudad, club.altitud,
        )

        sj["zonas_presencia"] = self.zonas.calcular(
            jugador.zonas, club.zonas_requeridas,
        )

        sj["viabilidad"] = self.viabilidad.calcular(
            jugador.meses_contrato,
            jugador.tiene_clausula,
            jugador.clausula_nivel,
        )

        # Modelo de juego (interpretativo)
        sj["modelo_juego"] = self.modelo_juego.calcular(
            club.compat_tactica_ofensiva,
            club.compat_tactica_defensiva,
            club.compat_tactica_transicion,
        )

        # ── Scores club ─────────────────────────────────────────
        sc = {}

        sc["entorno_competitivo"] = self.entorno.calcular(
            club.liga, club.posicion_tabla,
            club.total_equipos_liga,
            club.tiene_copa, club.tiene_internacional,
        )

        # Perfil requerido: edad ideal según proyecto, rol y minutos proyectados
        sc["perfil_jugador"] = self.perfil.calcular(
            jugador.edad, "titular_indiscutible",
            club.pct_minutos_proyectados,
            100.0,
        )

        # Compatibilidad estadística vs umbrales del club
        umbrales_club = dict(club.umbrales_estadisticos) if club.umbrales_estadisticos else {}
        if club.stats_aggregadas_raw and not umbrales_club:
            datos_club = parsear_sofascore(club.stats_aggregadas_raw)
            if datos_club:
                umbrales_club = calcular_umbrales_auto(
                    datos_club, club.liga, club.posicion_requerida,
                )
        if umbrales_club:
            umbral_promedio = sum(umbrales_club.values()) / len(umbrales_club)
        else:
            umbral_promedio = 6.0
        sc["estadisticas"] = umbral_promedio

        sc["fisico_salud"]    = sj["fisico_salud"]
        sc["adaptacion"]      = sj["adaptacion"]
        sc["zonas_presencia"] = sj["zonas_presencia"]
        sc["viabilidad"]      = sj["viabilidad"]

        sc["modelo_juego"] = sj["modelo_juego"]

        sc["proyecto"] = self.proyecto.calcular(
            club.alineacion_edad_horizonte,
            club.alineacion_perfil_modo,
            club.proyeccion_continuidad,
        )

        sc["actualidad"] = self.actualidad.calcular(
            club.posicion_tabla, club.total_equipos_liga,
            club.victorias_recientes, club.empates_recientes,
            club.derrotas_recientes, club.tiene_copa,
            club.tiene_internacional,
        )

        # ── Compatibilidades por módulo ─────────────────────────
        compatibilidades = {
            "entorno_competitivo": compatibilidad_modulo(sj["entorno_competitivo"], sc["entorno_competitivo"]),
            "perfil_jugador":      compatibilidad_modulo(sj["perfil_jugador"],      sc["perfil_jugador"]),
            "estadisticas":        min(sj["estadisticas"] / max(sc["estadisticas"], 0.1), 1.0),
            "fisico_salud":        compatibilidad_modulo(sj["fisico_salud"],        sc["fisico_salud"]),
            "adaptacion":          compatibilidad_modulo(sj["adaptacion"],          sc["adaptacion"]),
            "zonas_presencia":     (sj["zonas_presencia"] - 1) / 9,
            "modelo_juego":        (sj["modelo_juego"] - 1) / 9,
            "viabilidad":          compatibilidad_modulo(sj["viabilidad"],          sc["viabilidad"]),
        }

        # ── Score final por perfil con pesos dinámicos y penalización ──
        def score_perfil(p):
            pesos = pesos_activos[p]
            raw = sum(compatibilidades[m] * pesos[m] for m in compatibilidades) * 100
            return round(raw * (1 - penalizacion), 2)

        resultado = Resultado(
            nombre_jugador    = jugador.nombre,
            nombre_club       = club.nombre,
            valor_mercado     = jugador.valor_mercado,
            perfil_evaluacion = perfil_evaluacion,
            compatibilidades  = compatibilidades,
            scores_jugador    = sj,
            scores_club       = sc,
            nivel_brecha      = nivel_brecha,
            delta_coef        = delta_coef,
            penalizacion_aplicada = penalizacion,
            factor_contexto_global = factor_contexto_global,
            confiabilidad_estadisticas = confiabilidad_est,
            score_rendimiento_inmediato = score_perfil("rendimiento_inmediato"),
            score_potencial_mediano     = score_perfil("potencial_mediano_plazo"),
            score_bajo_riesgo           = score_perfil("bajo_riesgo_fracaso"),
        )

        mapa = {
            "rendimiento_inmediato":   resultado.score_rendimiento_inmediato,
            "potencial_mediano_plazo": resultado.score_potencial_mediano,
            "bajo_riesgo_fracaso":     resultado.score_bajo_riesgo,
        }
        resultado.score_final = mapa.get(perfil_evaluacion, resultado.score_rendimiento_inmediato)

        return resultado
