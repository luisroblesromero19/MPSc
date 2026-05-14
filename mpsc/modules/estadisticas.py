"""
MPSc — modules/estadisticas.py
Módulo: Estadísticas del jugador con normalización z-score
"""
from config import ESTADISTICAS_REFERENCIA, PESOS_ESTADISTICAS
from utils.normalizacion import convertir_por_90, normalizar_metrica


class ModuloEstadisticas:

    def _calcular_derivadas(self, datos: dict, minutos: float) -> dict:
        """Calcula métricas derivadas (porcentajes y valores por 90) a partir de datos brutos."""
        d = {}

        # Por 90 minutos para métricas que tienen clave _90 en referencia
        metricas_por_90 = [
            "goles", "tiros", "tiros_puerta", "toques_area", "faltas_rec",
            "despejes", "intercepciones", "entradas", "pases_prog",
            "carreras_prog", "pases_clave", "llegadas_area",
            "recuperaciones", "presiones", "salvadas", "salidas", "gc",
        ]
        for k in metricas_por_90:
            if k in datos:
                d[f"{k}_90"] = convertir_por_90(datos[k], minutos)

        # Porcentajes
        if datos.get("tiros_rec", 0) > 0:
            d["save_pct"] = (datos.get("salvadas", 0) / datos["tiros_rec"]) * 100

        if datos.get("da_disputados", 0) > 0:
            d["da_pct"] = (datos.get("da_ganados", 0) / datos["da_disputados"]) * 100

        if datos.get("dt_disputados", 0) > 0:
            d["dt_pct"] = (datos.get("dt_ganados", 0) / datos["dt_disputados"]) * 100

        if datos.get("do_disputados", 0) > 0:
            d["do_pct"] = (datos.get("do_ganados", 0) / datos["do_disputados"]) * 100

        if datos.get("dd_disputados", 0) > 0:
            d["dd_pct"] = (datos.get("dd_ganados", 0) / datos["dd_disputados"]) * 100

        if datos.get("pases_int", 0) > 0:
            d["pases_pct"] = (datos.get("pases_comp", 0) / datos["pases_int"]) * 100

        if datos.get("pases_l_int", 0) > 0:
            d["pases_largos_pct"] = (datos.get("pases_l_comp", 0) / datos["pases_l_int"]) * 100

        if datos.get("regates_int", 0) > 0:
            d["regates_pct"] = (datos.get("regates_ok", 0) / datos["regates_int"]) * 100

        if datos.get("centros", 0) > 0:
            d["centros_pct"] = (datos.get("centros_comp", 0) / datos["centros"]) * 100

        if datos.get("tiros", 0) > 0:
            d["conversion_pct"] = (datos.get("tiros_puerta", 0) / datos["tiros"]) * 100

        if datos.get("presiones", 0) > 0 and datos.get("presiones_ok", 0) > 0:
            d["presiones_pct"] = (datos["presiones_ok"] / datos["presiones"]) * 100

        # Merge pre-computed percentage values from datos (e.g. from Sofascore parse)
        # that weren't already computed because raw numerator/denominator weren't available
        pct_keys = ["save_pct", "da_pct", "dt_pct", "do_pct", "dd_pct",
                     "pases_pct", "pases_largos_pct", "regates_pct",
                     "centros_pct", "conversion_pct", "presiones_pct"]
        for k in pct_keys:
            if k not in d and k in datos:
                d[k] = datos[k]

        return d

    def _obtener_referencia(self, liga: str, posicion: str) -> dict:
        """Devuelve los datos de referencia (mu/sigma) para liga+posición."""
        ref_liga = ESTADISTICAS_REFERENCIA.get(liga, {})
        ref_pos  = ref_liga.get(posicion, {})

        # Fallback: si no hay datos específicos para esa liga, usar liga_mx
        if not ref_pos:
            ref_pos = ESTADISTICAS_REFERENCIA.get("liga_mx", {}).get(posicion, {})

        return ref_pos

    def calcular(self, posicion: str, liga: str, coef_liga: float,
                 datos_brutos: dict, minutos: float) -> tuple[float, dict]:
        """
        Retorna (score_total, detalle_por_metrica)
        detalle: {metrica: {valor_90: x, mu: y, sigma: z, score: w}}
        """
        derivadas  = self._calcular_derivadas(datos_brutos, minutos)
        referencia = self._obtener_referencia(liga, posicion)
        pesos      = PESOS_ESTADISTICAS.get(posicion, {})

        scores_ponderados = []
        suma_pesos        = 0.0
        detalle           = {}

        for metrica, peso in pesos.items():
            if metrica not in referencia:
                continue
            if metrica not in derivadas:
                continue

            valor = derivadas[metrica]
            mu    = referencia[metrica]["mu"]
            sigma = referencia[metrica]["sigma"]
            score = normalizar_metrica(valor, mu, sigma, coef_liga)

            detalle[metrica] = {
                "valor": round(valor, 3),
                "mu": mu,
                "sigma": sigma,
                "score": score,
                "peso": peso,
            }
            scores_ponderados.append(score * peso)
            suma_pesos += peso

        if suma_pesos == 0:
            return 5.0, {}

        score_total = sum(scores_ponderados) / suma_pesos
        return round(score_total, 2), detalle
