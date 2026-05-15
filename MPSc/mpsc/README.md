# MPSc — Modelo Predictivo de Scouting
## v1.0

Sistema de evaluación de compatibilidad jugador ↔ club destino para equipos de scouting de fútbol.

---

## Requisitos

- Python 3.10 o superior
- No requiere librerías externas para la versión base

Para el calibrador (opcional):
```bash
pip install pandas
```

---

## Instalación y uso

```bash
# Clonar o descomprimir el proyecto
cd mpsc

# Ejecutar
python main.py
```

---

## Estructura del proyecto

```
mpsc/
├── main.py                     # Punto de entrada
├── calculadora.py              # Orquestador del cálculo final
├── config.py                   # Coeficientes, pesos y datos de referencia
│
├── models/
│   ├── jugador.py              # Clase Jugador
│   ├── club.py                 # Clase Club
│   └── resultado.py            # Clase Resultado
│
├── modules/
│   ├── entorno.py              # Módulo entorno competitivo
│   ├── perfil.py               # Módulo perfil del jugador
│   ├── estadisticas.py         # Módulo estadísticas + z-score
│   ├── fisico.py               # Módulo físico y salud
│   ├── adaptacion.py           # Módulo adaptación
│   ├── zonas.py                # Módulo zonas + similitud coseno
│   ├── tactico.py              # Módulos interpretativos (juego, proyecto, actualidad)
│   └── viabilidad.py           # Módulo viabilidad contractual
│
└── utils/
    ├── input_helper.py         # Entrada de datos con colores y cancha visual
    ├── display.py              # Presentación de resultados
    ├── normalizacion.py        # Z-score, conversión 1-10, compatibilidad
    ├── formulario_jugador.py   # Flujo completo de captura del jugador
    ├── formulario_club.py      # Flujo completo de captura del club
    └── calibrador.py           # Herramienta para calcular mu/sigma desde CSV
```

---

## Tres perfiles de evaluación

| Perfil | Descripción |
|---|---|
| `rendimiento_inmediato` | El jugador debe aportar desde la primera jornada |
| `potencial_mediano_plazo` | Apuesta a futuro, jugador en desarrollo |
| `bajo_riesgo_fracaso` | Prioridad en seguridad física y adaptación |

---

## Actualizar datos de referencia (mu/sigma) con datos reales

1. Descarga tablas de estadísticas por posición desde [FBref](https://fbref.com) en formato CSV.
2. Ejecuta el calibrador:

```bash
python utils/calibrador.py \
  --csv ruta/al/archivo.csv \
  --liga liga_mx \
  --posicion delantero_centro \
  --min-min 500
```

3. Copia el bloque generado en `ESTADISTICAS_REFERENCIA` dentro de `config.py`.

---

## Zonas del campo

El campo se divide en 18 zonas:

```
┌──────────┬──────────┬──────────┐
│  Zona 1  │  Zona 2  │  Zona 3  │  ← Ataque
├──────────┼──────────┼──────────┤
│  Zona 4  │  Zona 5  │  Zona 6  │  ← Med. alto
├──────────┼──────────┼──────────┤
│  Zona 7  │  Zona 8  │  Zona 9  │  ← Med. bajo
├──────────┼──────────┼──────────┤
│  Zona 10 │  Zona 11 │  Zona 12 │  ← Med. def.
├──────────┼──────────┼──────────┤
│  Zona 13 │  Zona 14 │  Zona 15 │  ← Defensa
├──────────┼──────────┼──────────┤
│  Zona 16 │  Zona 17 │  Zona 18 │  ← Área propia
└──────────┴──────────┴──────────┘
  Izquierda   Centro    Derecha
```

---

## Fórmulas clave

**Z-score:** `z = (valor_jugador - μ) / σ`

**Z ajustado por liga:** `z_adj = z × coeficiente_liga`

**Conversión a escala 1-10:** `score = ((z_adj + 3) / 6) × 9 + 1`

**Compatibilidad por módulo:** `compat = 1 - (|score_j - score_c| / 10)`

**Score final:** `Σ (compatibilidad_módulo × peso_módulo)`

---

## Notas

- Los valores de μ y σ precargados son estimados representativos basados en el caso de ejemplo del modelo (Óscar Fuentes / Club Atlético Morelia).
- Para uso en producción se recomienda calibrar con datos reales usando `utils/calibrador.py`.
- La regresión lineal para aprendizaje automático de pesos está planificada para v2.0.
