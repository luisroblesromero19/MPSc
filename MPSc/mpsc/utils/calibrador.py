"""
MPSc — utils/calibrador.py
Herramienta para calcular mu y sigma reales desde archivos CSV de FBref.

Uso:
    python utils/calibrador.py --csv ruta/al/archivo.csv --liga liga_mx --posicion delantero_centro

El archivo CSV debe tener una columna 'posicion' y las columnas de métricas.
Genera el bloque de configuración listo para pegar en config.py
"""
import sys
import os
import json

try:
    import pandas as pd
except ImportError:
    print("Este script requiere pandas. Instala con: pip install pandas")
    sys.exit(1)

# Métricas esperadas por posición (deben coincidir con columnas del CSV)
METRICAS_ESPERADAS = {
    "delantero_centro": ["goles_90", "tiros_90", "tiros_puerta_90", "toques_area_90",
                         "da_pct", "faltas_rec_90", "pases_pct", "xg_90", "conversion_pct"],
    "extremo":          ["tiros_90", "tiros_puerta_90", "regates_pct", "pases_clave_90",
                         "centros_pct", "carreras_prog_90", "pases_pct", "xg_90", "xa_90"],
    "mediocampista_central": ["pases_prog_90", "pases_clave_90", "carreras_prog_90",
                              "llegadas_area_90", "recuperaciones_90", "tiros_90",
                              "pases_pct", "xg_90", "xa_90"],
    "mediocampista_defensivo": ["intercepciones_90", "entradas_90", "presiones_90",
                                "presiones_pct", "pases_prog_90", "recuperaciones_90",
                                "da_pct", "pases_pct"],
    "central":          ["despejes_90", "intercepciones_90", "entradas_90", "pases_prog_90",
                         "da_pct", "dt_pct", "pases_pct", "pases_largos_pct"],
    "lateral":          ["centros_pct", "pases_prog_90", "carreras_prog_90", "do_pct",
                         "dd_pct", "intercepciones_90", "pases_pct"],
    "portero":          ["salvadas_90", "gc_90", "save_pct", "salidas_90", "pases_pct", "da_pct"],
}


def calcular_estadisticas(csv_path: str, liga: str, posicion: str,
                           columna_posicion: str = "posicion",
                           min_minutos: int = 500) -> dict:
    """
    Lee un CSV de FBref y calcula mu y sigma para cada métrica.

    Args:
        csv_path: ruta al archivo CSV
        liga: clave de liga (ej: "liga_mx")
        posicion: clave de posición (ej: "delantero_centro")
        columna_posicion: nombre de la columna que identifica la posición
        min_minutos: mínimo de minutos jugados para incluir al jugador

    Returns:
        dict con estructura lista para pegar en ESTADISTICAS_REFERENCIA de config.py
    """
    df = pd.read_csv(csv_path)

    print(f"  Filas totales en CSV: {len(df)}")

    # Filtrar por posición si la columna existe
    if columna_posicion in df.columns:
        df = df[df[columna_posicion].str.lower().str.contains(posicion.replace("_", " "), na=False)]
        print(f"  Filas tras filtrar por posición '{posicion}': {len(df)}")

    # Filtrar por mínimo de minutos si la columna existe
    if "minutos" in df.columns:
        df = df[df["minutos"] >= min_minutos]
        print(f"  Filas tras filtrar por minutos >= {min_minutos}: {len(df)}")

    if len(df) == 0:
        print("  ⚠ Sin datos suficientes para calcular estadísticas.")
        return {}

    metricas = METRICAS_ESPERADAS.get(posicion, [])
    resultado = {}

    for metrica in metricas:
        if metrica not in df.columns:
            print(f"  ⚠ Columna '{metrica}' no encontrada en CSV. Saltando.")
            continue
        serie = df[metrica].dropna()
        if len(serie) < 5:
            print(f"  ⚠ Muy pocos datos para '{metrica}' ({len(serie)} valores). Saltando.")
            continue
        resultado[metrica] = {
            "mu":    round(float(serie.mean()), 4),
            "sigma": round(float(serie.std()), 4),
        }
        print(f"  ✓ {metrica:<30} μ={resultado[metrica]['mu']:.4f}  σ={resultado[metrica]['sigma']:.4f}")

    return resultado


def generar_bloque_config(liga: str, posicion: str, estadisticas: dict) -> str:
    """Genera el bloque de texto listo para pegar en config.py"""
    lineas = [f'        "{posicion}": {{']
    for metrica, vals in estadisticas.items():
        lineas.append(f'            "{metrica}":' + ' ' * (28 - len(metrica)) +
                      f'{{"mu": {vals["mu"]}, "sigma": {vals["sigma"]}}},')
    lineas.append('        },')
    bloque = "\n".join(lineas)
    return f'\n    "{liga}": {{\n{bloque}\n    }}\n'


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Calibrador MPSc — calcula mu y sigma desde CSV de FBref")
    parser.add_argument("--csv",      required=True, help="Ruta al archivo CSV")
    parser.add_argument("--liga",     required=True, help="Clave de liga (ej: liga_mx)")
    parser.add_argument("--posicion", required=True, help="Clave de posición (ej: delantero_centro)")
    parser.add_argument("--col-pos",  default="posicion", help="Columna de posición en el CSV")
    parser.add_argument("--min-min",  type=int, default=500, help="Mínimo de minutos jugados")
    parser.add_argument("--output",   default=None, help="Archivo de salida JSON (opcional)")
    args = parser.parse_args()

    print(f"\n{'═'*55}")
    print(f"  MPSc Calibrador — {args.liga} / {args.posicion}")
    print(f"{'═'*55}\n")

    stats = calcular_estadisticas(args.csv, args.liga, args.posicion,
                                  args.col_pos, args.min_min)

    if stats:
        bloque = generar_bloque_config(args.liga, args.posicion, stats)
        print(f"\n{'─'*55}")
        print("  Bloque para pegar en config.py → ESTADISTICAS_REFERENCIA:")
        print(f"{'─'*55}")
        print(bloque)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({args.liga: {args.posicion: stats}}, f, indent=2, ensure_ascii=False)
            print(f"  Guardado en: {args.output}")
    else:
        print("  No se generaron estadísticas. Verifica el CSV y los parámetros.")
