import re
from config import (
    COEFICIENTES_CONTRIBUCION_ALFA, MAPEO_METRICAS_SOFASCORE,
    MAPEO_SOFASCORE_JUGADOR,
    REFERENCIA_CLUBES, MIN_PROMEDIO_PARTIDO,
    PESOS_ESTADISTICAS,
)
from utils.normalizacion import z_score, z_a_escala_10


def _coincide_metrica_amplio(clave_texto: str, patron: str) -> bool:
    cl = clave_texto.lower().strip()
    pa = patron.lower().strip()
    if cl == pa:
        return True
    palabras_cl = set(cl.replace("/", " ").replace("-", " ").split())
    palabras_pa = set(pa.replace("/", " ").replace("-", " ").split())
    comunes = palabras_cl & palabras_pa
    palabras_ban = {"per", "game", "partido", "por", "%", "a", "de", "en", "el", "la", "los", "las", "the", "and", "of", "in"}
    importantes = comunes - palabras_ban
    return len(importantes) >= 2


def extraer_estadisticas_jugador(texto: str) -> dict:
    """
    Parsea texto Sofascore de un jugador y extrae estadísticas en formato
    {clave_interna: valor_total} para usar como jugador.estadisticas.
    Convierte valores 'per_game' a totales usando partidos encontrados.
    """
    if not texto or not texto.strip():
        return {}
    datos = parsear_sofascore(texto)
    if not datos:
        return {}
    partidos = None
    for clave in ("matches", "partidos", "appearances", "apariciones"):
        if clave in datos:
            partidos = int(datos[clave])
            break
    resultado = {}
    matched_keys = set()

    def _set_valor(clave_sofascore, interna, tipo, valor):
        if clave_sofascore in matched_keys:
            return
        matched_keys.add(clave_sofascore)
        if tipo == "total":
            resultado[interna] = int(valor) if valor == int(valor) else valor
        elif tipo == "per_game":
            if partidos and partidos > 0:
                resultado[interna] = round(valor * partidos, 2)
        elif tipo == "percentage":
            resultado[interna] = valor

    mapping_items = list(MAPEO_SOFASCORE_JUGADOR.items())

    # First pass: exact match
    for clave_sofascore, valor in datos.items():
        for patron, (interna, tipo) in mapping_items:
            if clave_sofascore == patron.lower().strip():
                _set_valor(clave_sofascore, interna, tipo, valor)
                break

    # Second pass: substring match (patron in clave or vice versa)
    for clave_sofascore, valor in datos.items():
        for patron, (interna, tipo) in mapping_items:
            pa_lower = patron.lower().strip()
            if pa_lower in clave_sofascore or clave_sofascore in pa_lower:
                _set_valor(clave_sofascore, interna, tipo, valor)
                break

    # Third pass: word intersection match
    for clave_sofascore, valor in datos.items():
        for patron, (interna, tipo) in mapping_items:
            if _coincide_metrica_amplio(clave_sofascore, patron):
                _set_valor(clave_sofascore, interna, tipo, valor)
                break

    if "da_perdidos" in resultado and "da_ganados" in resultado:
        resultado["da_disputados"] = resultado["da_ganados"] + resultado["da_perdidos"]
        del resultado["da_perdidos"]
    if "dt_perdidos" in resultado and "dt_ganados" in resultado:
        resultado["dt_disputados"] = resultado["dt_ganados"] + resultado["dt_perdidos"]
        del resultado["dt_perdidos"]
    return resultado


def parsear_sofascore(texto: str) -> dict:
    if not texto or not texto.strip():
        return {}
    limpio = texto.strip()
    resultados = {}
    for line in limpio.splitlines():
        line = line.strip()
        if not line:
            continue

        # Formato: "Metrica total (porcentaje%)"
        m_paren = re.match(r'^(.+?)\s+([\d.]+)\s*\(([\d.]+)%\)\s*$', line)
        if m_paren:
            nombre = re.sub(r'\s+', ' ', m_paren.group(1).strip().lower())
            resultados[nombre] = float(m_paren.group(3))
            continue

        # Formato: "Metrica valor%"  (sin parentesis)
        m_pct = re.match(r'^(.+?)\s+([\d.]+)%\s*$', line)
        if m_pct:
            nombre = re.sub(r'\s+', ' ', m_pct.group(1).strip().lower())
            resultados[nombre] = float(m_pct.group(2))
            continue

        # Formato: "Metrica valor"
        m_simple = re.match(r'^(.+?)\s+([\d.]+)\s*$', line)
        if m_simple:
            nombre = re.sub(r'\s+', ' ', m_simple.group(1).strip().lower())
            try:
                resultados[nombre] = float(m_simple.group(2))
            except ValueError:
                pass

    return resultados


def _coincide_metrica(clave_sofascore: str, data_key: str) -> bool:
    if clave_sofascore in data_key or data_key in clave_sofascore:
        return True
    palabras_data = set(data_key.replace("/", " ").replace("-", " ").split())
    palabras_map = set(clave_sofascore.replace("/", " ").replace("-", " ").split())
    comunes = palabras_data & palabras_map
    palabras_importantes = {"goals", "balls", "duels", "aerial", "passes", "dribbles",
                             "recovered", "interceptions", "possession", "shots",
                             "long", "crosses", "saves", "scored", "game", "won",
                             "accurate"}
    return len(comunes & palabras_importantes) >= 2


def _buscar_metrica_interna(sofascore_key: str) -> str | None:
    for clave_sofascore, (interna, _) in MAPEO_METRICAS_SOFASCORE.items():
        if _coincide_metrica(clave_sofascore, sofascore_key):
            return interna
    return None


def normalizar_metricas_club(datos: dict, partidos: int | None = None) -> dict:
    normalizadas = {}
    if partidos is None:
        partidos = int(datos.get("matches", datos.get("partidos", 1)))
    if partidos <= 0:
        partidos = 1
    for clave, valor in datos.items():
        interna = _buscar_metrica_interna(clave)
        if interna is None:
            continue
        if "%" in clave:
            normalizadas[interna] = valor
        else:
            normalizadas[interna] = valor
    return normalizadas


def _obtener_referencia_clubes(liga: str) -> dict:
    ref = REFERENCIA_CLUBES.get(liga, {})
    if not ref:
        ref = REFERENCIA_CLUBES.get("liga_mx", {})
    return ref


def calcular_umbrales_auto(datos_club: dict, liga: str, posicion: str) -> dict:
    ref = _obtener_referencia_clubes(liga)
    alfas = {}
    umbrales = {}
    for metrica_club in MAPEO_METRICAS_SOFASCORE.values():
        interna, _ = metrica_club
        alfas[interna] = COEFICIENTES_CONTRIBUCION_ALFA.get(interna, {}).get(posicion, 0.5)
    for clave_sofascore, (interna, direccion) in MAPEO_METRICAS_SOFASCORE.items():
        encontrada = False
        valor = None
        for dk, dv in datos_club.items():
            if _coincide_metrica(clave_sofascore, dk):
                valor = dv
                encontrada = True
                break
        if not encontrada or valor is None:
            continue
        ref_metrica = ref.get(interna)
        if not ref_metrica:
            continue
        z = z_score(valor, ref_metrica["mu"], ref_metrica["sigma"])
        score = z_a_escala_10(z)
        alfa = alfas.get(interna, 0.5)
        umbral_ajustado = round(score * alfa, 2)
        umbrales[interna] = min(10.0, max(1.0, umbral_ajustado))
    return umbrales


def calcular_indice_exigencia(z: float) -> float:
    return max(0.0, min(2.0, (z + 3.0) / 3.0))


def calcular_contribucion_relativa(
    metrica_interna: str,
    valor_jugador_90: float,
    valor_club_pp: float,
    posicion: str,
) -> float:
    if valor_club_pp <= 0:
        return 1.0
    alfa = COEFICIENTES_CONTRIBUCION_ALFA.get(metrica_interna, {}).get(posicion, 0.5)
    if alfa <= 0:
        return 1.0
    contribucion_bruta = valor_jugador_90 / valor_club_pp
    return contribucion_bruta / alfa


def calcular_factor_contexto(
    datos_club_origen: dict,
    detalle_estadisticas: dict,
    liga_origen: str,
    posicion: str,
) -> tuple[float, float, float]:
    """
    detalle_estadisticas: dict con formato {metrica: {valor: ..., peso: ...}}
    (proviene del ModuloEstadisticas, contiene valores por 90 ya calculados)
    """
    ref = _obtener_referencia_clubes(liga_origen)
    factores = []
    pesos_usados = []
    pesos_posicion = PESOS_ESTADISTICAS.get(posicion, {})
    for clave_sofascore, (interna, direccion) in MAPEO_METRICAS_SOFASCORE.items():
        valor_club = None
        for dk, dv in datos_club_origen.items():
            if _coincide_metrica(clave_sofascore, dk):
                valor_club = dv
                break
        if valor_club is None:
            continue
        ref_metrica = ref.get(interna)
        if not ref_metrica:
            continue
        z = z_score(valor_club, ref_metrica["mu"], ref_metrica["sigma"])
        indice = calcular_indice_exigencia(z)
        det = detalle_estadisticas.get(interna)
        if det is None:
            continue
        metrica_jug_90 = det.get("valor", 0)
        if metrica_jug_90 <= 0:
            continue
        contrib = calcular_contribucion_relativa(interna, metrica_jug_90, valor_club, posicion)
        if indice <= 0:
            continue
        factor = contrib / indice
        peso = det.get("peso", pesos_posicion.get(interna, 0.1))
        factores.append(factor)
        pesos_usados.append(peso)
    if not factores:
        return 1.0, 0.0, 1.0
    suma_pesos = sum(pesos_usados)
    if suma_pesos <= 0:
        factor_global = sum(factores) / len(factores)
    else:
        factor_global = sum(f * p for f, p in zip(factores, pesos_usados)) / suma_pesos
    correccion = max(-0.5, min(0.5, (factor_global - 1.0) * 0.5))
    confiabilidad = max(0.5, min(1.0, 1.0 / (abs(1.0 - factor_global) + 1.0)))
    return round(factor_global, 4), round(correccion, 4), round(confiabilidad, 4)


def aplicar_correccion_stats(score_base: float, correccion: float) -> float:
    return max(1.0, min(10.0, score_base + correccion))
