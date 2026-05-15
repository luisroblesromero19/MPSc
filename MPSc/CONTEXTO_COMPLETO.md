# MPSc — Modelo Predictivo de Scouting (v1.0)

## CONTEXTO COMPLETO DEL PROYECTO

> Este documento describe exhaustivamente qué hace el sistema, cómo funciona,
> qué fórmulas utiliza, cómo se relacionan los módulos y cómo se usa.
> Está diseñado para que un agente IA pueda entender el proyecto en su totalidad.

---

## ÍNDICE

1. [VISIÓN GENERAL](#1-visión-general)
2. [ESTRUCTURA DEL PROYECTO](#2-estructura-del-proyecto)
3. [FLUJO DE CÁLCULO](#3-flujo-de-cálculo)
4. [MÓDULOS DE SCORE (SJ y SC)](#4-módulos-de-score-sj-y-sc)
   - 4.1 Entorno Competitivo
   - 4.2 Perfil del Jugador
   - 4.3 Estadísticas (z-score)
   - 4.4 Físico y Salud
   - 4.5 Adaptación
   - 4.6 Zonas de Presencia
   - 4.7 Modelo de Juego (Táctico)
   - 4.8 Proyecto Deportivo
   - 4.9 Actualidad del Club
   - 4.10 Viabilidad Contractual
   - 4.11 Contexto de Equipo (Sofascore)
5. [COMPATIBILIDAD POR MÓDULO](#5-compatibilidad-por-módulo)
6. [PESOS POR NIVEL DE BRECHA Y PERFIL](#6-pesos-por-nivel-de-brecha-y-perfil)
7. [SCORE FINAL](#7-score-final)
8. [NORMALIZACIÓN](#8-normalización)
9. [MODELOS DE DATOS](#9-modelos-de-datos)
10. [INTERFACES DE USUARIO](#10-interfaces-de-usuario)
11. [CORRECCIONES APLICADAS](#11-correcciones-aplicadas)
12. [EJEMPLO COMPLETO](#12-ejemplo-completo)

---

## 1. VISIÓN GENERAL

**MPSc** es un sistema de evaluación de compatibilidad entre un **jugador de fútbol**
y un **club destino**. Responde a la pregunta:

> *"¿Qué tan compatible es este jugador con este club, dadas las características
> de ambos y el contexto competitivo?"*

El sistema considera **8 módulos de evaluación**:
entorno, perfil, estadísticas, físico, adaptación, zonas, modelo de juego
y viabilidad.

Para cada módulo se calculan dos scores (en escala 1-10):
- **sj** = score del *jugador* (qué tan bueno es el jugador en ese aspecto)
- **sc** = score del *club* (qué tan exigente/ideal es el club en ese aspecto)

A partir de sj y sc se calcula una **compatibilidad** (0.00 a 1.00) por módulo.
Las compatibilidades se ponderan con pesos que varían según:

1. **Nivel de brecha** (1, 2, 3) — diferencia entre coeficientes de liga
2. **Perfil de evaluación** (rendimiento_inmediato, potencial_mediano_plazo, bajo_riesgo_fracaso)

Se aplica una penalización por brecha y se obtienen **3 scores finales** (0-100).

---

## 2. ESTRUCTURA DEL PROYECTO

```
MPSc/
├── verificar_correcciones.py    Script de verificación matemática
│
└── mpsc/                        Paquete principal
    ├── __init__.py
    ├── main.py                   Entry point CLI (interactive console)
    ├── webapp.py                 Entry point web (HTTP server, port 8765)
    ├── config.py                 Constantes, pesos, datos de referencia
    ├── calculadora.py            ORQUESTADOR — coordina todo
    │
    ├── models/                   Modelos de datos (dataclasses)
    │   ├── jugador.py            Datos del jugador evaluado
    │   ├── club.py               Datos del club destino
    │   └── resultado.py          Resultado de la evaluación + interpretación
    │
    ├── modules/                  Módulos de cálculo
    │   ├── entorno.py            Entorno competitivo
    │   ├── perfil.py             Perfil base del jugador
    │   ├── estadisticas.py       Estadísticas (z-score vs referencia)
    │   ├── fisico.py             Físico, lesiones, carga
    │   ├── adaptacion.py         Adaptación cultural/idiomática/climática
    │   ├── zonas.py              Zonas de presencia (coseno)
    │   ├── tactico.py            Modelo de juego, proyecto, actualidad
    │   ├── viabilidad.py         Viabilidad contractual
    │   └── contexto_equipo.py    Parsing Sofascore, contexto de equipo
    │
    └── utils/                    Utilidades
        ├── input_helper.py       CLI: colores, inputs validados, campo ASCII
        ├── display.py            CLI: mostrar resultados con barras
        ├── formulario_jugador.py CLI: formulario interactivo del jugador
        ├── formulario_club.py    CLI: formulario interactivo del club
        ├── normalizacion.py      z-score, escala 1-10, compatibilidad
        ├── reporte_html.py       Generador de reporte HTML (Chart.js)
        └── calibrador.py         Calibración desde CSV (FBref)
```

---

## 3. FLUJO DE CÁLCULO

El flujo completo se ejecuta en `Calculadora.calcular()` (`calculadora.py`):

```
  jugador (Jugador) + club (Club) + perfil_evaluacion (str)
         │
         ▼
  [1] Determinar nivel_brecha (1, 2, 3)
      según |coef_liga_jugador - coef_liga_club|
         │
         ▼
  [2] Seleccionar pesos_activos según nivel_brecha + perfil_evaluacion
         │
         ▼
  [3] Calcular sj (scores del jugador) para cada módulo:
      ├── sj["entorno_competitivo"] = ModuloEntorno.calcular(liga, pos_tabla, ...)
      ├── sj["perfil_jugador"]      = ModuloPerfil.calcular(edad, rol, minutos...)
      ├── sj["estadisticas"]        = ModuloEstadisticas.calcular(pos, liga, stats...)
      ├── sj["fisico_salud"]        = ModuloFisico.calcular(lesiones, carga, altitud...)
      ├── sj["adaptacion"]          = ModuloAdaptacion.calcular(idioma, pais, clima...)
      ├── sj["zonas_presencia"]     = ModuloZonas.calcular(zonas_jug, zonas_club)
      ├── sj["modelo_juego"]        = ModuloModeloJuego.calcular(of, def, trans)
      └── sj["viabilidad"]          = ModuloViabilidad.calcular(contrato, clausula)
         │
         ▼
  [4] Aplicar corrección por contexto de equipo (Sofascore)
      → Ajusta sj["estadisticas"] si hay datos del club de origen
         │
         ▼
  [5] Calcular sc (scores del club) para cada módulo:
      ├── sc["entorno_competitivo"] = ModuloEntorno.calcular(liga club, ...)
      ├── sc["perfil_jugador"]      = ModuloPerfil.calcular(edad, "titular", pct_min...)
      ├── sc["estadisticas"]        = promedio de umbrales (Sofascore o manual)
      ├── sc["fisico_salud"]        = sj["fisico_salud"]  (se reusa)
      ├── sc["adaptacion"]          = sj["adaptacion"]    (se reusa)
      ├── sc["zonas_presencia"]     = sj["zonas_presencia"] (se reusa)
      ├── sc["modelo_juego"]        = sj["modelo_juego"]  (se reusa)
      ├── sc["viabilidad"]          = sj["viabilidad"]    (se reusa)
      ├── sc["proyecto"]            = ModuloProyecto.calcular(edad, perfil, continuidad)
      └── sc["actualidad"]          = ModuloActualidadClub.calcular(pos, forma, comps)
         │
         ▼
  [6] Calcular compatibilidades (0.00 a 1.00) por módulo:
      ├── compatibilidad simétrica:  1 - |sj - sc| / 10   (para 7 módulos)
      ├── compatibilidad asimétrica: min(sj / sc, 1.0)    (estadísticas)
      ├── zonas_presencia:          (sj - 1) / 9
      └── modelo_juego:             (sj - 1) / 9
         │
         ▼
  [7] Calcular score_perfil(perfil_evaluacion):
      raw = Σ(compatibilidad[m] × peso[m]) × 100
      score = raw × (1 - penalizacion_brecha)
         │
         ▼
  [8] Devolver Resultado con 3 scores + compatibilidades + sj + sc
```

### Cálculo de los SCORES DEL CLUB (sc)

Algunos scores del club se **reusan** de los del jugador:

| Módulo | sc proviene de... | Razón |
|--------|-------------------|-------|
| entorno_competitivo | Cálculo propio con datos del club | El club tiene su propia liga/posición |
| perfil_jugador | Cálculo propio: `edad`, `"titular_indiscutible"`, `pct_minutos_proyectados` | El club busca un perjo ideal |
| estadisticas | **Umbral promedio** (de Sofascore auto o manual) | El club tiene exigencias estadísticas |
| fisico_salud | **= sj["fisico_salud"]** | El club evalúa al mismo jugador |
| adaptacion | **= sj["adaptacion"]** | Es la misma adaptación |
| zonas_presencia | **= sj["zonas_presencia"]** | Son las mismas zonas |
| modelo_juego | **= sj["modelo_juego"]** | Es el mismo modelo |
| viabilidad | **= sj["viabilidad"]** | Es la misma viabilidad |
| proyecto | Cálculo propio con datos del club | Proyecto deportivo del club |
| actualidad | Cálculo propio con datos del club | Actualidad del club |

---

## 4. MÓDULOS DE SCORE (SJ y SC)

### 4.1 Entorno Competitivo (`ModuloEntorno`)

**Archivo:** `modules/entorno.py`
**Propósito:** Puntúa la fortaleza del entorno competitivo (liga, posición en tabla, copas).

```
score_liga = coef_liga × 10

percentil_tabla = 1 - (posicion - 1) / (total_equipos - 1)

score_tabla = 
  9.0  si percentil ≥ 0.80
  7.0  si percentil ≥ 0.60
  6.0  si percentil ≥ 0.40
  4.5  si percentil ≥ 0.25
  2.0  en otro caso

score_competencias =
  10.0 si tiene_copa Y tiene_internacional
  7.0  si solo tiene_copa
  5.0  si percentil ≥ 0.40 (sin copas)
  3.0  en otro caso

score_final = score_liga × 0.50 + score_tabla × 0.30 + score_comp × 0.20
```

**Rango:** 1.0 — 10.0

**Ejemplo:**
- Liga MX (coef=1.00), posición 3ª de 18, con copa e internacional
  → score_liga = 10.0, percentil=0.88 → score_tabla=9.0, score_comp=10.0
  → score = 10.0×0.5 + 9.0×0.3 + 10.0×0.2 = 5.0+2.7+2.0 = 9.70

---

### 4.2 Perfil del Jugador (`ModuloPerfil`)

**Archivo:** `modules/perfil.py`
**Propósito:** Puntúa el perfil base: edad, rol en el equipo y minutos jugados.

```
score_edad(edad):
  5.0  si 17 ≤ edad ≤ 19
  8.0  si 20 ≤ edad ≤ 23
  10.0 si 24 ≤ edad ≤ 27
  7.0  si 28 ≤ edad ≤ 30
  4.0  en otro caso

score_rol(rol):
  10  si "titular_indiscutible"
  8   si "titular_con_competencia"
  6   si "rotacion_habitual"
  4   si "suplente"
  1   si "sin_minutos"

score_minutos(pct):
  10.0 si pct ≥ 90%
  8.0  si pct ≥ 75%
  6.0  si pct ≥ 60%
  4.0  si pct ≥ 45%
  2.0  en otro caso
  donde pct = (minutos_jugados / minutos_posibles) × 100

score = s_edad × 0.25 + s_rol × 0.35 + s_minutos × 0.40

Si filtro_duro_ok es False (posición no coincide): score = min(score, 3.0)
```

**Rango:** 1.0 — 10.0

**Para el club (sc):** se calcula sobre el *jugador* pero usando:
- `rol = "titular_indiscutible"` (el club quiere un titular)
- `minutos_jugados = pct_minutos_proyectados` (lo que el club proyecta darle)
- `minutos_posibles = 100.0`
- `filtro_duro_ok = True`

**Ejemplo:**
- Edad 25 (s_edad=10), titular indiscutible (s_rol=10), 85% min (s_min=8.0)
  → score = 10×0.25 + 10×0.35 + 8.0×0.4 = 2.5+3.5+3.2 = 9.20

---

### 4.3 Estadísticas (`ModuloEstadisticas`)

**Archivo:** `modules/estadisticas.py`
**Propósito:** Puntúa el rendimiento estadístico del jugador vs datos de referencia
de su liga y posición, usando normalización z-score.

**Pipeline por cada métrica:**
```
1. Derivar métricas:
   - Per-90:  metrica_90 = (total / minutos) × 90
   - Porcentajes:  pct = numerador / denominador × 100
     (save_pct, da_pct, dt_pct, pases_pct, regates_pct, etc.)

2. z = (valor_90 - mu) / sigma        # z-score
   z_adj = z × coef_liga              # ajuste por liga
   z_clamp = clamp(z_adj, -3.0, 3.0)  # truncar a [-3, 3]
   score_metrica = ((z_clamp + 3) / 6) × 9 + 1   # mapeo [-3,3] → [1,10]

3. score_total = Σ(score_metrica_m × peso_m) / Σ(pesos_m)
```

**Fórmula de z → escala 10:**
```
         (z + 3)
score = ──────── × 9 + 1
            6
```

Correspondencia:
| z-score | score |
|---------|-------|
| -3.0 | 1.0 |
| -2.0 | 2.5 |
| -1.0 | 4.0 |
| 0.0 | 5.5 |
| +1.0 | 7.0 |
| +2.0 | 8.5 |
| +3.0 | 10.0 |

**Pesos por posición:** definidos en `config.py` como `PESOS_ESTADISTICAS`.
Cada posición tiene 6-7 métricas con pesos que suman 1.0.

**Referencia:** `ESTADISTICAS_REFERENCIA` en config.py, con datos mu/sigma
por liga y posición. Si no hay datos para una liga, se usa liga_mx como fallback.

**Rango:** 1.0 — 10.0

**Ejemplo:**
- Delantero centro en Liga MX: goles_90=0.42, mu=0.35, sigma=0.12, coef=1.0
  → z = (0.42-0.35)/0.12 = 0.583, z_adj=0.583
  → score = ((0.583+3)/6)×9+1 = 6.37

---

### 4.4 Físico y Salud (`ModuloFisico`)

**Archivo:** `modules/fisico.py`
**Propósito:** Evalúa estado físico: historial de lesiones, tipo de lesión,
carga de minutos y penalización por altitud.

```
score_historial:
  10.0 si 0 lesiones
  8.0  si 1 lesión
  6.0  si 2 lesiones
  4.0  si 3 lesiones
  2.0  si 4+

score_tipo(tipo_lesion, semanas_baja):
  Base = según tipo: (ninguna=10, muscular=6, ligamento=4, fractura=7)
  Penalización por semanas:
    0 si ≤3, 1 si ≤6, 2 si ≤12, 3 si >12
  score = max(1.0, base - penalizacion)

score_carga(pct):
  5.0             si pct < 60%   [baja carga]
  5.0 + (pct-60)×0.5  si 60% ≤ pct < 70%   [transición lineal]
  10.0            si 70% ≤ pct ≤ 85%  [carga óptima]
  8.0             si 86% ≤ pct ≤ 92%  [carga alta]
  6.0             si pct > 92%        [sobrecarga]
  donde pct = (minutos_jugados / minutos_posibles) × 100

penalizacion_altitud(diff):
  0.0  si diff < 500
  0.5  si diff < 1500
  1.0  si diff < 2500
  2.0  en otro caso

score_base = s_hist × 0.50 + s_tipo × 0.30 + s_carga × 0.20
score_final = max(1.0, score_base - penalizacion_altitud)
```

**Rango:** 1.0 — 10.0

---

### 4.5 Adaptación (`ModuloAdaptacion`)

**Archivo:** `modules/adaptacion.py`
**Propósito:** Evalúa la facilidad de adaptación considerando idioma,
cultura (países cercanos) y clima (diferencia de altitud).

```
score_idioma:
  10.0 si mismo idioma
  7.0  si par cercano (español↔portugués, inglés↔inglés)
  4.0  si diferente pero con experiencia extranjera
  1.0  si diferente y sin experiencia

score_cultura(pais_jug, pais_club):
  10.0 si mismo país
  7.0  si ambos latinoamericanos
  4.0  si ambos occidentales (Latam + Europa/EEUU/Canadá)
  1.0  en otro caso

score_clima(diff_altitud):
  10.0 si diff < 300
  8.0  si diff < 800
  6.0  si diff < 1500
  4.0  si diff < 2500
  1.0  en otro caso

score = s_idioma × 0.40 + s_cultura × 0.35 + s_clima × 0.25
```

**Rango:** 1.0 — 10.0

---

### 4.6 Zonas de Presencia (`ModuloZonas`)

**Archivo:** `modules/zonas.py`
**Propósito:** Mide la similitud entre las zonas donde juega el jugador
y las zonas que el club necesita reforzar, usando **similitud coseno**.

El campo se divide en **18 zonas** (numeradas 1-18):

```
  ┌──────┬──────┬──────┐
  │  1   │  2   │  3   │   Ataque
  ├──────┼──────┼──────┤
  │  4   │  5   │  6   │   Medio alto
  ├──────┼──────┼──────┤
  │  7   │  8   │  9   │   Medio bajo
  ├──────┼──────┼──────┤
  │ 10   │ 11   │ 12   │   Medio defensivo
  ├──────┼──────┼──────┤
  │ 13   │ 14   │ 15   │   Defensa
  ├──────┼──────┼──────┤
  │ 16   │ 17   │ 18   │   Área propia
  └──────┴──────┴──────┘
```

**Construcción del vector:** hasta 5 zonas rankeadas con pesos [5,4,3,2,1].

```
vector = [0] × 18
para i, zona in enumerate(zonas[:5]):
    vector[zona-1] += PESOS_RANKING[i]  # [5,4,3,2,1]

similitud = coseno(vec_jugador, vec_club)
          = Σ(a·b) / (√Σa² × √Σb²)

score = similitud × 9 + 1
```

**Rango:** 1.0 (completamente diferente) — 10.0 (idéntico)

---

### 4.7 Modelo de Juego / Módulo Táctico (`ModuloModeloJuego`)

**Archivo:** `modules/tactico.py`
**Propósito:** Score interpretativo (ingresado manualmente por el scout)
que evalúa la compatibilidad táctica en 3 fases.

```
score = (score_ofensiva + score_defensiva + score_transicion) / 3
```

**Rango:** 1.0 — 10.0

Nota: Los scores de compatibilidad táctica (1-10) son ingresados manualmente
por el scout en el formulario del club, NO se calculan automáticamente.

---

### 4.8 Proyecto Deportivo (`ModuloProyecto`)

**Archivo:** `modules/tactico.py`
**Propósito:** Score interpretativo del proyecto deportivo del club.

```
score = (alineacion_edad_horizonte + alineacion_perfil_modo + proyeccion_continuidad) / 3
```

**Rango:** 1.0 — 10.0
**Uso:** Solo se calcula para sc (score del club). No existe sj de proyecto.

---

### 4.9 Actualidad del Club (`ModuloActualidadClub`)

**Archivo:** `modules/tactico.py`
**Propósito:** Evalúa la actualidad deportiva del club: posición en tabla,
forma reciente y competencias activas.

```
score_posicion:
  Igual que entorno (percentil → score discreto)

score_forma:
  puntos = victorias×3 + empates×1
  pct_puntos = puntos / ((V+E+D) × 3)
  score = (pct_puntos × 9) + 1

score_competencias:
  10.0 si tiene_copa Y tiene_internacional
  7.0  si solo tiene_copa
  5.0  en otro caso

score = s_pos × 0.50 + s_forma × 0.30 + s_comp × 0.20
```

**Rango:** 1.0 — 10.0
**Uso:** Solo se calcula para sc (score del club).

---

### 4.10 Viabilidad Contractual (`ModuloViabilidad`)

**Archivo:** `modules/viabilidad.py`
**Propósito:** Evalúa qué tan factible es la contratación según
el contrato actual y la cláusula de rescisión.

```
score_contrato(meses):
  10.0 si meses ≤ 6    [contrato corto, fácil]
  8.0  si meses ≤ 12
  6.0  si meses ≤ 18
  4.0  si meses ≤ 24
  2.0  si > 24         [contrato largo, difícil]

score_clausula:
  10.0 si no tiene cláusula
  8.0  si cláusula "accesible"
  5.0  si cláusula "alta"

score = s_contrato × 0.60 + s_clausula × 0.40
```

**Rango:** 1.0 — 10.0

---

### 4.11 Contexto de Equipo (`contexto_equipo.py`)

**Archivo:** `modules/contexto_equipo.py`
**Propósito:** Parsea datos Sofascore (texto plano), calcula umbrales
automáticos del club, y corrige el score de estadísticas del jugador
según el contexto de su club de origen.

**Funciones principales:**

#### `extraer_estadisticas_jugador(texto: str) -> dict`
Parsea texto Sofascore del jugador usando 3 pasadas de matching
(exacto, substring, intersección de palabras). Convierte valores
"per_game" a totales usando el número de partidos encontrado.

#### `parsear_sofascore(texto: str) -> dict`
Parsea genérico de Sofascore. 3 formatos:
- `"Metrica valor (porcentaje%)"` → guarda el porcentaje
- `"Metrica valor%"` → guarda el valor como float
- `"Metrica valor"` → guarda el valor como float

#### `calcular_umbrales_auto(datos_club, liga, posicion) -> dict`
Para cada métrica del club, calcula:
```
z = z_score(valor_club, mu_referencia, sigma_referencia)
score_raw = z_a_escala_10(z)           # [1, 10]
alfa = coeficiente_contribucion[posicion][metrica]  # [0, 1]
umbral = score_raw × alfa
umbral_clamped = clamp(umbral, 1.0, 10.0)
```

#### `calcular_factor_contexto(datos_club_origen, detalle_estadisticas, liga, posicion)`
Para cada métrica compartida entre jugador y club:
```
indice_exigencia = clamp((z + 3) / 3, 0, 2)   # proxy de dificultad
contribucion_relativa = (valor_jugador_90 / valor_club_pp) / alfa
factor = contribucion_relativa / indice_exigencia
```

Promedio ponderado de factores → `factor_global`.
```
correccion = clamp((factor_global - 1.0) × 0.5, -0.5, 0.5)
confiabilidad = clamp(1.0 / (|1.0 - factor_global| + 1.0), 0.5, 1.0)
```

#### `aplicar_correccion_stats(score_base, correccion)`
```
score_corregido = clamp(score_base + correccion, 1.0, 10.0)
```

---

## 5. COMPATIBILIDAD POR MÓDULO

La compatibilidad transforma el par (sj, sc) —ambos en escala 1-10—
en un valor entre 0.00 y 1.00.

### 5.1 Compatibilidad Simétrica (7 módulos)

Usada por: entorno, perfil, físico, adaptación, viabilidad (y proyecto/actualidad como sc).

```
compatibilidad = 1 - |sj - sc| / 10
```

**Lógica:** Mide qué tan cerca están sj y sc. Si coinciden perfectamente
(sj=sc) → 1.00. Si están en extremos opuestos (sj=1, sc=10 o viceversa) → 0.00.

**Ejemplos:**
| sj | sc | compatibilidad |
|----|-----|--------------|
| 7.0 | 7.0 | 1.000 |
| 7.0 | 8.5 | 0.850 |
| 7.0 | 3.0 | 0.600 |
| 1.0 | 10.0 | 0.100 |
| 10.0 | 1.0 | 0.100 |

### 5.2 Compatibilidad Asimétrica (estadísticas)

```
compatibilidad = min(sj_estadisticas / sc_estadisticas, 1.0)
```

**Lógica:** Solo mide si el jugador alcanza el umbral del club.
Si sj ≥ sc → 1.00 (no importa cuánto lo supere).
Si sj < sc → penaliza proporcionalmente.

**Ejemplos:**
| sj | sc | compatibilidad |
|----|-----|--------------|
| 7.0 | 7.0 | 1.000 |
| 9.0 | 7.0 | 1.000 (supera, no penaliza) |
| 5.0 | 7.0 | 0.714 |
| 2.0 | 8.0 | 0.250 |

### 5.3 Compatibilidad por Rango Lineal (zonas y modelo_juego)

```
compatibilidad_zonas      = (sj - 1) / 9    # [1,10] → [0.00, 1.00]
compatibilidad_modelo_juego = (sj - 1) / 9  # [1,10] → [0.00, 1.00]
```

**Lógica:** Estos módulos no tienen un sc independiente; la compatibilidad
es directamente proporcional al score del jugador.

**Ejemplos:**
| sj | compatibilidad |
|----|---------------|
| 1 | 0.000 |
| 3 | 0.222 |
| 5 | 0.444 |
| 8 | 0.778 |
| 10 | 1.000 |

### 5.4 Resumen de Métodos

| Módulo | Método | Fórmula |
|--------|--------|---------|
| entorno_competitivo | Simétrico | 1 - \|sj - sc\| / 10 |
| perfil_jugador | Simétrico | 1 - \|sj - sc\| / 10 |
| estadisticas | Asimétrico | min(sj / sc, 1.0) |
| fisico_salud | Simétrico | 1 - \|sj - sc\| / 10 |
| adaptacion | Simétrico | 1 - \|sj - sc\| / 10 |
| zonas_presencia | Rango directo | (sj - 1) / 9 |
| modelo_juego | Rango directo | (sj - 1) / 9 |
| viabilidad | Simétrico | 1 - \|sj - sc\| / 10 |

---

## 6. PESOS POR NIVEL DE BRECHA Y PERFIL

### 6.1 Coeficientes de Liga y Brecha

```
COEFICIENTES_LIGA:
  liga_mx:            1.00
  liga_argentina:     0.95
  mls:                0.90
  liga_colombiana:    0.85
  liga_chilena:       0.80  (no está en coef pero referenciada)
  liga_expansion_mx:  0.75
  liga_peruana:       0.75
  segunda_division_mx:0.60

Δcoef = |coef_jugador - coef_club|

UMBRAL_BRECHA_MEDIA = 0.20
UMBRAL_BRECHA_ALTA  = 0.35

nivel_brecha:
  1  si Δcoef ≤ 0.20
  2  si 0.20 < Δcoef ≤ 0.35
  3  si Δcoef > 0.35

PENALIZACION_BRECHA:
  nivel_1: 0.00
  nivel_2: 0.08  (8%)
  nivel_3: 0.15  (15%)
```

### 6.2 Pesos por Nivel y Perfil

Cada perfil define la importancia relativa de cada módulo.
Los pesos SIEMPRE suman 1.00 (corregido).

#### NIVEL 1 — Brecha baja (Δcoef ≤ 0.20)

| Módulo | Rendimiento Inmediato | Potencial Mediano | Bajo Riesgo |
|--------|:---------------------:|:-----------------:|:-----------:|
| entorno_competitivo | 0.22 | 0.12 | 0.10 |
| perfil_jugador | 0.15 | 0.13 | 0.12 |
| estadisticas | 0.16 | 0.13 | 0.15 |
| fisico_salud | 0.12 | 0.12 | 0.25 |
| adaptacion | 0.10 | 0.15 | 0.15 |
| zonas_presencia | 0.10 | 0.10 | 0.08 |
| modelo_juego | 0.10 | 0.10 | 0.10 |
| viabilidad | 0.05 | 0.15 | 0.05 |
| **Suma** | **1.00** | **1.00** | **1.00** |

#### NIVEL 2 — Brecha media (0.20 < Δcoef ≤ 0.35)
*Respecto a Nivel 1: estadísticas -8pp, modelo_juego +5pp, entorno +3pp*

| Módulo | Rendimiento Inmediato | Potencial Mediano | Bajo Riesgo |
|--------|:---------------------:|:-----------------:|:-----------:|
| entorno_competitivo | 0.25 | 0.15 | 0.13 |
| perfil_jugador | 0.15 | 0.15 | 0.12 |
| estadisticas | 0.08 | 0.03 | 0.07 |
| fisico_salud | 0.12 | 0.12 | 0.25 |
| adaptacion | 0.10 | 0.15 | 0.15 |
| zonas_presencia | 0.10 | 0.10 | 0.08 |
| modelo_juego | 0.15 | 0.15 | 0.15 |
| viabilidad | 0.05 | 0.15 | 0.05 |
| **Suma** | **1.00** | **1.00** | **1.00** |

#### NIVEL 3 — Brecha alta (Δcoef > 0.35)
*Respecto a Nivel 1: estadísticas -14pp, modelo_juego +8pp, entorno +6pp*

| Módulo | Rendimiento Inmediato | Potencial Mediano | Bajo Riesgo |
|--------|:---------------------:|:-----------------:|:-----------:|
| entorno_competitivo | 0.28 | 0.17 | 0.16 |
| perfil_jugador | 0.15 | 0.15 | 0.12 |
| estadisticas | 0.02 | 0.02 | 0.01 |
| fisico_salud | 0.12 | 0.12 | 0.25 |
| adaptacion | 0.10 | 0.15 | 0.15 |
| zonas_presencia | 0.10 | 0.10 | 0.08 |
| modelo_juego | 0.18 | 0.15 | 0.18 |
| viabilidad | 0.05 | 0.14 | 0.05 |
| **Suma** | **1.00** | **1.00** | **1.00** |

---

## 7. SCORE FINAL

### 7.1 Cálculo del Score por Perfil

```
raw = Σ(compatibilidad_m × peso_m)    # para los 8 módulos
                                     # resultado en [0.00, 1.00]
score_perfil = raw × 100 × (1 - penalización_brecha)
```

Donde `penalización_brecha` es:
- Nivel 1: 0% → score_perfil = raw × 100
- Nivel 2: 8% → score_perfil = raw × 100 × 0.92
- Nivel 3: 15% → score_perfil = raw × 100 × 0.85

**Rango:** 0.00 — 100.00

### 7.2 Interpretación del Score Final

La interpretación depende del **nivel de brecha**:

**Nivel 1 (brecha baja):**
| Score | Interpretación |
|-------|---------------|
| ≥ 85 | MUY ALTA — Candidato prioritario |
| ≥ 70 | ALTA — Candidato recomendado |
| ≥ 55 | MODERADA — Candidato con reservas |
| ≥ 40 | BAJA — Brechas importantes |
| < 40 | MUY BAJA — No recomendado |

**Nivel 2 (brecha media):**
| Score | Interpretación |
|-------|---------------|
| ≥ 85 | MUY ALTA — Candidato recomendado con monitoreo |
| ≥ 70 | ALTA — Candidato con reservas |
| ≥ 55 | MODERADA — Alto riesgo |
| ≥ 40 | BAJA — No recomendado |
| < 40 | MUY BAJA — No recomendado |

**Nivel 3 (brecha alta):**
| Score | Interpretación |
|-------|---------------|
| ≥ 85 | MUY ALTA — Candidato con reservas serias |
| ≥ 70 | ALTA — Alto riesgo |
| ≥ 55 | MODERADA — No recomendado |
| ≥ 40 | BAJA — No recomendado |
| < 40 | MUY BAJA — No recomendado |

Colores asociados:
| Score | Color |
|-------|-------|
| ≥ 85 | #22c55e (verde) |
| ≥ 70 | #84cc16 (verde claro) |
| ≥ 55 | #f59e0b (ámbar) |
| ≥ 40 | #f97316 (naranja) |
| < 40 | #ef4444 (rojo) |

### 7.3 Producto Final

El `Resultado` contiene 3 scores (uno por perfil) y un `score_final`
que corresponde al perfil seleccionado en la evaluación.

---

## 8. NORMALIZACIÓN

### 8.1 `convertir_por_90(total, minutos) -> float`

```
si minutos ≤ 0:  return 0.0
si no:           return (total / minutos) × 90
```

Convierte estadísticas totales a valor por cada 90 minutos.

### 8.2 `z_score(valor, mu, sigma) -> float`

```
si sigma ≤ 0:  return 0.0
si no:         return (valor - mu) / sigma
```

### 8.3 `ajustar_por_liga(z, coef) -> float`

```
return z × coef
```

### 8.4 `z_a_escala_10(z) -> float`

```
z = clamp(z, -3.0, 3.0)
return ((z + 3) / 6) × 9 + 1
```

Mapeo:
- z = -3 → score = 1
- z = 0 → score = 5.5
- z = +3 → score = 10

### 8.5 Pipeline Completo: `normalizar_metrica(valor, mu, sigma, coef) -> float`

```
z = z_score(valor, mu, sigma)
z_adj = ajustar_por_liga(z, coef)
return z_a_escala_10(z_adj)
```

### 8.6 `compatibilidad_modulo(score_a, score_b) -> float`

```
return 1 - (|score_a - score_b| / 10)
```

---

## 9. MODELOS DE DATOS

### 9.1 `Jugador` (dataclass) — `models/jugador.py`

**Campos de identificación:**
- `nombre`, `fecha_nacimiento`, `edad`, `pais_origen`, `ciudad_actual`
- `idioma`, `experiencia_extranjero` (bool)
- `valor_mercado` (str, ej: "5M €"), `meses_contrato` (int)
- `tiene_clausula` (bool), `clausula_nivel` ("accesible" | "alta")

**Campos del club actual:**
- `club_actual`, `liga`, `posicion_tabla` (int), `total_equipos_liga` (int)
- `tiene_copa` (bool), `tiene_internacional` (bool)
- `sistema_tactico_club`, `estilo_ofensivo`, `estilo_defensivo`, `estilo_transicion`
- `altitud_ciudad` (float, metros)

**Campos de rendimiento:**
- `minutos_jugados` (float), `minutos_posibles` (float)
- `posicion` (str, una de POSICIONES), `rol` (str)
- `estadisticas` (dict: clave_interna → valor)
- `num_lesiones` (int), `tipo_lesion` (str), `semanas_baja_promedio` (float)
- `zonas` (list[int], hasta 5)

**Campos Sofascore:**
- `sofascore_jugador_raw` (str), `stats_club_origen_raw` (str)

**Campos de resultado:**
- `scores` (dict, llenado por la calculadora)

### 9.2 `Club` (dataclass) — `models/club.py`

**Campos de identificación:**
- `nombre`, `ciudad`, `pais`, `idioma`, `altitud` (float)
- `liga`, `posicion_tabla` (int), `total_equipos_liga` (int)

**Campos de forma:**
- `victorias_recientes`, `empates_recientes`, `derrotas_recientes` (últimos 5)
- `tiene_copa` (bool), `tiene_internacional` (bool)

**Campos tácticos (ingresados por scout):**
- `sistema_tactico`, `estilo_ofensivo`, `estilo_defensivo`, `estilo_transicion`
- `posicion_requerida`, `perfil_tactico`
- `zonas_requeridas` (list[int])
- `jugadores_en_posicion` (int)
- `pct_minutos_proyectados` (float, 0-100)
- `horizonte_anios` (int), `modo_competitivo` (str)
- `umbrales_estadisticos` (dict, manual o auto)

**Campos Sofascore:**
- `stats_aggregadas_raw` (str)

**Campos interpretativos (scout, 1-10):**
- `compat_tactica_ofensiva`, `compat_tactica_defensiva`, `compat_tactica_transicion`
- `alineacion_edad_horizonte`, `alineacion_perfil_modo`, `proyeccion_continuidad`

**Campos de resultado:**
- `scores` (dict)

### 9.3 `Resultado` (dataclass) — `models/resultado.py`

**Campos:**
- `nombre_jugador`, `nombre_club`, `valor_mercado`
- `perfil_evaluacion` (str: "rendimiento_inmediato"|"potencial_mediano_plazo"|"bajo_riesgo_fracaso")
- `compatibilidades` (dict: módulo → float 0-1)
- `scores_jugador` (dict: módulo → float 1-10)
- `scores_club` (dict: módulo → float 1-10)
- `nivel_brecha` (1|2|3), `delta_coef` (float), `penalizacion_aplicada` (float)
- `factor_contexto_global` (float), `confiabilidad_estadisticas` (float)
- `score_rendimiento_inmediato` (float, 0-100)
- `score_potencial_mediano` (float, 0-100)
- `score_bajo_riesgo` (float, 0-100)
- `score_final` (float, 0-100)

**Métodos:**
- `interpretacion()` → str: texto según score + nivel_brecha
- `color_interpretacion()` → str: hex color del score

---

## 10. INTERFACES DE USUARIO

### 10.1 CLI — `main.py`

Ejecución: `python mpsc/main.py`

Menú interactivo que:
1. Captura datos del jugador (`formulario_jugador.py`)
2. Captura datos del club (`formulario_club.py`)
3. Selecciona perfil de evaluación
4. Ejecuta el cálculo
5. Muestra resultados con barras ASCII y colores
6. Opción de abrir reporte HTML

### 10.2 Web — `webapp.py`

Ejecución: `python mpsc/webapp.py` → http://localhost:8765

Servidor HTTP que sirve una interfaz HTML con:
- Formularios para jugador y club
- Parseo automático de texto Sofascore (con override manual)
- Chart.js: gráfico radar + barras horizontales
- Resultados en tiempo real vía POST /calcular

### 10.3 Reporte HTML — `reporte_html.py`

Genera un archivo HTML temporal con:
- Gráfico radar de compatibilidades
- Gráfico de barras horizontal con scores detallados
- Score final con color e interpretación
- Se abre automáticamente en el navegador

---

## 11. CORRECCIONES APLICADAS

### 11.1 Pesos sumaban 1.10 → corregido a 1.00

**Problema:** Los 9 perfiles en los 3 niveles de brecha tenían pesos
que sumaban 1.10. Inflación sistemática del ~10%.

**Impacto:** Jugador promedio con compatibilidad 70% obtenía 77%.
Score máximo posible en Nivel 1 era 110%.

**Corrección:** Distribución de -0.10 entre los pesos más grandes de cada perfil.

### 11.2 Cálculo cuadrático en perfil del club

**Problema en `calculadora.py`:** Se usaba `pct × pct / 100` en vez de `pct`.

**Impacto:** Con 70% proyectado, se pasaba 49 en vez de 70,
subestimando el score del club consistentemente.

**Corrección:** Se cambió a `pct` directo.

### 11.3 modelo_juego rango incompleto

**Problema en `calculadora.py`:** Se usaba `sj / 10` → rango [0.10, 1.00].

**Impacto:** Con el peor score posible (1), daba compatibilidad 0.10
en vez de 0.00, inconsistente con zonas_presencia que sí usaba `(sj-1)/9`.

**Corrección:** Se cambió a `(sj - 1) / 9` → rango [0.00, 1.00].

### 11.4 Salto brusco en carga física

**Problema en `fisico.py`:** Entre 69% y 70% de minutos, el score
saltaba de 5.0 a 10.0 (Δ = 5 pts por 1%).

**Corrección:** Se agregó interpolación lineal `5 + (pct-60) × 0.5`
para el rango 60-70%.

### 11.5 Inconsistencia documentada en estadísticas

**Problema:** Estadísticas usa `min(sj/sc, 1.0)` (asimétrico)
mientras los otros módulos usan `1 - |sj-sc|/10` (simétrico).

**Decisión:** Se documenta como intencional — superar el umbral
estadístico del club no debería penalizar.

---

## 12. EJEMPLO COMPLETO

### Datos de entrada

**Jugador:** Juan Pérez, 25 años, delantero centro
- Liga: liga_mx (coef=1.00), posición 3ª de 18
- Rol: titular_indiscutible, 85% minutos jugados
- Estadísticas: goles_90=0.42, tiros_90=2.1, ...
- Lesiones: 1 muscular, 4 semanas baja
- Idiomas: español, mexicano
- Meses contrato: 10, sin cláusula
- Zonas: [14, 11, 8, 5, 2]

**Club:** Club América, liga_mx (coef=1.00)
- Posición: 1ª de 18, con copa e internacional
- Busca: delantero centro, pct_minutos_proyectados=75%
- Zonas requeridas: [14, 11, 8, 5]
- Tactical: of=8, def=7, trans=8
- Proyecto: edad=9, perfil=8, continuidad=8

### Cálculo paso a paso

**Nivel de brecha:** |1.00 - 1.00| = 0.00 → Nivel 1 (penalización=0%)

**Scores jugador (sj):**

| Módulo | Cálculo | Resultado |
|--------|---------|:---------:|
| entorno | score_liga=10, score_tabla=9, score_comp=10 → 10×0.5+9×0.3+10×0.2 | **9.70** |
| perfil | s_edad(25)=10, s_rol(titular)=10, s_min(85%)=8 → 10×0.25+10×0.35+8×0.4 | **9.20** |
| estadisticas | normalizar_metrica(goles_90=0.42, mu=0.35, sigma=0.12, coef=1) → z=0.583 → | **6.37** |
| fisico | s_hist(1)=8, s_tipo(muscular,4sem)=5, s_carga(85%)=10 → 8×0.5+5×0.3+10×0.2 | **7.50** (sin penalización altitud) |
| adaptacion | s_idioma(español/español)=10, s_cultura(Mex/Mex)=10, s_clima(2240/2240)=10 | **10.00** |
| zonas | coseno([5,0,0,4,3,0,0,2,0,0,1,0,0,0,0,0,0,0], [5,0,0,4,3,0,0,2,0,0,1,0,0,0,0,0,0,0])=1.0 | **10.00** |
| modelo_juego | (8+7+8)/3 | **7.67** |
| viabilidad | s_contrato(10meses)=8, s_clausula(no)=10 → 8×0.6+10×0.4 | **8.80** |

**Scores club (sc):**

| Módulo | Cálculo | Resultado |
|--------|---------|:---------:|
| entorno | score_liga=10, score_tabla(1/18)=9, score_comp(copa+intl)=10 | **9.70** |
| perfil | s_edad(25)=10, s_rol(titular)=10, s_min(75%/100)=8 → 10×0.25+10×0.35+8×0.4 | **9.20** |
| estadisticas | umbral_promedio (ej. umbrales auto) | **7.50** |
| proyecto | (9+8+8)/3 | **8.33** |
| actualidad | s_pos(1/18)=9, s_forma(ej. 4V/1E/0D=9.0), s_comp=10 → 9×0.5+9×0.3+10×0.2 | **9.20** |

**Compatibilidades:**

| Módulo | sj | sc | Fórmula | Resultado |
|--------|:--:|:--:|---------|:---------:|
| entorno | 9.70 | 9.70 | 1-\|9.70-9.70\|/10 | **1.000** |
| perfil | 9.20 | 9.20 | 1-\|9.20-9.20\|/10 | **1.000** |
| estadisticas | 6.37 | 7.50 | min(6.37/7.50, 1) | **0.849** |
| fisico | 7.50 | 7.50 | 1-\|7.50-7.50\|/10 | **1.000** |
| adaptacion | 10.00 | 10.00 | 1-\|10.00-10.00\|/10 | **1.000** |
| zonas | 10.00 | — | (10-1)/9 | **1.000** |
| modelo_juego | 7.67 | — | (7.67-1)/9 | **0.741** |
| viabilidad | 8.80 | 8.80 | 1-\|8.80-8.80\|/10 | **1.000** |

**Score final (perfil "rendimiento_inmediato", Nivel 1):**

```
raw = (1.000 × 0.22) + (1.000 × 0.15) + (0.849 × 0.16) + (1.000 × 0.12)
    + (1.000 × 0.10) + (1.000 × 0.10) + (0.741 × 0.10) + (1.000 × 0.05)

raw = 0.220 + 0.150 + 0.136 + 0.120 + 0.100 + 0.100 + 0.074 + 0.050
raw = 0.950

score = 0.950 × 100 × (1 - 0.00) = 95.00
```

**Interpretación:** ≥ 85 → "MUY ALTA — Candidato prioritario"
**Color:** #22c55e (verde)
