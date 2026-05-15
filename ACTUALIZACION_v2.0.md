# MPSc — Actualización v2.0: Persistencia MySQL + Scouting Táctico Automático

## Documento de Arquitectura para Agentes

---

### 1. RESUMEN DE CAMBIOS (v1.1 + v2.0)

**v1.1 — Persistencia MySQL:**
- Capa de persistencia con SQLAlchemy ORM
- CRUD de jugadores + historial de temporadas
- Adaptadores ORM ↔ dataclass para compatibilidad con motor de cálculo

**v2.0 — Scouting Táctico Automático:**
- CRUD completo de clubes con estadísticas por temporada
- Perfil táctico automático del club desde stats brutas (12 dimensiones 0-10)
- Detector de necesidades tácticas basado en reglas heurísticas (7 reglas)
- Vectorización táctica de jugadores (10 dimensiones 0-1)
- Vector de necesidad del club
- Similitud coseno + compatibilidad táctica con ponderación por confianza
- Motor de búsqueda masiva: ScoutingService.buscar_jugadores_compatibles()

**NO se modificó ningún archivo existente del motor de cálculo original.**

---

### 2. ESTRUCTURA COMPLETA DEL PROYECTO

```
MPSc/
│
├── .env.example                         # Config MySQL
├── .env                                 # Config local
├── requirements.txt                     # Dependencias
├── alembic.ini                          # Config migraciones
│
├── verificar_correcciones.py            # Verificación matemática
├── CONTEXTO_COMPLETO.md                 # Documentación del motor de cálculo
├── ACTUALIZACION_v1.1.md                # Documentación v1.1
│
├── examples/
│   ├── demo_persistencia.py             # Demo CRUD jugadores (v1.1)
│   └── demo_scouting_automatico.py      # Demo búsqueda masiva (v2.0)
│
└── mpsc/                                # Paquete principal
    ├── config.py                        # SIN CAMBIOS
    ├── calculadora.py                   # SIN CAMBIOS
    ├── main.py                          # SIN CAMBIOS
    ├── webapp.py                        # SIN CAMBIOS
    │
    ├── models/                          # SIN CAMBIOS
    │   ├── jugador.py
    │   ├── club.py
    │   └── resultado.py
    │
    ├── modules/                         # SIN CAMBIOS (módulos originales)
    │   ├── entorno.py
    │   ├── perfil.py
    │   ├── estadisticas.py
    │   ├── fisico.py
    │   ├── adaptacion.py
    │   ├── zonas.py
    │   ├── tactico.py
    │   ├── viabilidad.py
    │   ├── contexto_equipo.py
    │   │
    │   ├── inferencia_tactica.py        ← NUEVO v2.0
    │   ├── detector_necesidades.py      ← NUEVO v2.0
    │   └── vectorizacion.py             ← NUEVO v2.0
    │
    ├── database/                        ← NUEVO v1.1
    │   ├── __init__.py
    │   ├── connection.py                # DatabaseManager, Base, init_db()
    │   ├── adapters.py                  # ORM ↔ dataclass Jugador
    │   ├── init_db.py                   # Script para crear tablas
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── jugador_model.py         # JugadorORM
    │   │   ├── temporada_model.py       # TemporadaORM
    │   │   ├── club_model.py            # ClubORM            ← NUEVO v2.0
    │   │   └── temporada_club_model.py  # TemporadaClubORM   ← NUEVO v2.0
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   ├── jugador_repository.py
    │   │   ├── temporada_repository.py
    │   │   ├── club_repository.py       ← NUEVO v2.0
    │   │   └── temporada_club_repository.py  ← NUEVO v2.0
    │   └── migrations/
    │       ├── env.py
    │       ├── script.py.mako
    │       └── versions/
    │           ├── 0001_initial.py      # jugadores + temporadas_jugador
    │           └── 0002_clubes.py       # clubes + temporadas_club  ← NUEVO v2.0
    │
    └── services/                        ← NUEVO
        ├── __init__.py
        ├── jugador_service.py
        ├── temporada_service.py
        ├── club_service.py              ← NUEVO v2.0
        └── scouting_service.py          ← NUEVO v2.0
```

---

### 3. TABLAS NUEVAS (v2.0)

#### 3.1 `clubes`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | INT (PK, autoincrement) | |
| nombre | VARCHAR(255) | Indexado |
| pais | VARCHAR(100) | |
| liga | VARCHAR(50) | Indexado |
| division | VARCHAR(50) | |
| temporada_actual | VARCHAR(20) | |
| entrenador | VARCHAR(255) | |
| sistema_tactico | VARCHAR(100) | |
| created_at | DATETIME | autogenerado |
| updated_at | DATETIME | autogenerado |

#### 3.2 `temporadas_club`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | INT (PK) | |
| club_id | INT (FK → clubes.id) | CASCADE |
| temporada | VARCHAR(20) | Indexado |
| partidos | INT | |
| goles_favor | INT | |
| goles_contra | INT | |
| asistencias | INT | |
| posesion | FLOAT | |
| pases_precisos | INT | |
| precision_pases | FLOAT | |
| balones_largos | INT | |
| precision_balones_largos | FLOAT | |
| centros | INT | |
| precision_centros | FLOAT | |
| regates | INT | |
| corners | INT | |
| tiros | INT | |
| tiros_puerta | INT | |
| porterias_cero | INT | |
| intercepciones | INT | |
| recuperaciones | INT | |
| errores_tiro | INT | |
| duelos_ganados | INT | |
| duelos_aereos | INT | |
| fueras_juego | INT | |
| faltas | INT | |
| amarillas | INT | |
| rojas | INT | |
| sofascore_raw | JSON | |
| metricas_ofensivas_json | JSON | |
| metricas_defensivas_json | JSON | |
| metricas_transicion_json | JSON | |
| created_at | DATETIME | |

---

### 4. MÓDULO: INFERENCIA TÁCTICA (`modules/inferencia_tactica.py`)

Convierte estadísticas crudas del club en un perfil táctico de 12 dimensiones,
cada una normalizada en rango 0-10.

#### `PerfilTacticoClub` (dataclass)

| Atributo | Rango | Fórmula Heurística |
|----------|-------|-------------------|
| `amplitud` | 0-10 | centros×4 + regates×3 + corners×3 normalizado |
| `verticalidad` | 0-10 | balones_largos×6 + fueras_juego×4 normalizado |
| `posesion` | 0-10 | posesion% / 55.0 × 10 |
| `intensidad_presion` | 0-10 | recuperaciones×6 + intercepciones×4 normalizado |
| `agresividad_defensiva` | 0-10 | faltas×0.4 + amarillas×0.4 + rojas×2.0 |
| `dependencia_bandas` | 0-10 | centros×6 + regates×2 + corners×2 normalizado |
| `progresion` | 0-10 | pases_precisos proxy |
| `control_juego` | 0-10 | posesion×0.5 + precision_pases×0.5 normalizado |
| `fragilidad_defensiva` | 0-10 | goles_contra×6 + errores_tiro×4 normalizado |
| `fragilidad_aerea` | 0-10 | duelos_aereos (inverso: pocos duelos = frágil) |
| `eficiencia_ofensiva` | 0-10 | (goles_favor / tiros) × 200 |
| `volumen_ofensivo` | 0-10 | tiros×6 + tiros_puerta×4 normalizado |

#### `inferir_perfil(stats: dict, partidos: int) -> PerfilTacticoClub`

Todas las fórmulas usan constantes configurables (`REF_POSESION`, `REF_CENTROS_PARTIDO`, etc.)
y funciones auxiliares `_a_10()` y `_por_partido()`.

---

### 5. MÓDULO: DETECTOR DE NECESIDADES (`modules/detector_necesidades.py`)

Sistema extensible basado en reglas heurísticas. Cada regla examina el
`PerfilTacticoClub` y produce una `NecesidadTactica` si se cumplen las condiciones.

#### `NecesidadTactica` (dataclass)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rol` | str | Posición requerida |
| `prioridad` | float | 0.0 - 1.0 |
| `motivo` | str | Explicación legible |
| `metricas_relacionadas` | List[str] | Métricas que dispararon la regla |

#### Reglas implementadas (7)

| # | Condición | Necesidad |
|---|-----------|-----------|
| 1 | volumen_ofensivo ≥ 6.0 Y eficiencia_ofensiva ≤ 4.5 | `delantero_centro` |
| 2 | posesion ≥ 6.5 Y progresion ≤ 5.0 | `mediocampista_central` (creativo) |
| 3 | fragilidad_aerea ≥ 6.5 | `central` (dominante aéreo) |
| 4 | amplitud ≤ 4.0 Y dependencia_bandas ≤ 4.0 | `extremo` (desborde) |
| 5 | amplitud ≤ 4.5 Y centros_pp bajos | `lateral` (ofensivo) |
| 6 | intensidad_presion ≤ 4.5 | `mediocampista_defensivo` |
| 7 | fragilidad_defensiva ≥ 6.0 Y 4.0 ≤ volumen ≤ 7.0 | `mediocampista_central` (box-to-box) |

Las reglas se agregan en `DetectorNecesidades._reglas()` como métodos.
El umbral de activación mínimo es configurable.

---

### 6. MÓDULO: VECTORIZACIÓN (`modules/vectorizacion.py`)

Genera vectores numéricos de 10 dimensiones (0-1) para similitud coseno.

#### `generar_vector_jugador(jugador: Jugador) -> List[float]`

| Dimensión | Fuente |
|-----------|--------|
| `finalizacion` | goles / tiros × 5 |
| `progresion` | pases_prog / pases_totales × 10 |
| `amplitud` | (centros + regates_int) / 100 |
| `recuperacion` | (recuperaciones + intercepciones) / 100 |
| `juego_aereo` | da_ganados / da_disputados × 2 |
| `regate` | regates_ok / regates_int × 2 |
| `creatividad` | (pases_clave + asistencias×2) / 50 |
| `intensidad` | (entradas + faltas_rec) / 80 |
| `movilidad` | Según rol (titular→0.9, suplente→0.3) |
| `disciplina_tactica` | 1.0 - faltas/60 |

#### `generar_vector_necesidad_club(perfil, necesidades) -> List[float]`

Inversa del perfil táctico: si al club le falta algo, la necesidad es alta.

| Dimensión | Fórmula |
|-----------|---------|
| `finalizacion` | (10 - eficiencia_ofensiva) / 10 |
| `progresion` | (10 - progresion) / 10 |
| `amplitud` | (10 - amplitud) / 10 |
| `recuperacion` | (10 - intensidad_presion) / 10 |
| `juego_aereo` | fragilidad_aerea / 10 |
| `regate` | (10 - dependencia_bandas) / 10 |
| `creatividad` | (10 - control_juego) / 10 |
| `intensidad` | (10 - intensidad_presion) / 10 |
| `movilidad` | verticalidad / 10 |
| `disciplina_tactica` | fragilidad_defensiva / 10 |

#### `similitud_coseno(vec_a, vec_b) -> float`

```
coseno = Σ(a·b) / (√Σa² × √Σb²)
```

#### `compatibilidad_tactica(jugador, perfil, necesidades) -> dict`

```
vec_jug = generar_vector_jugador(jugador)
vec_club = generar_vector_necesidad_club(perfil, necesidades)
sim = similitud_coseno(vec_jug, vec_club)
confianza = min(minutos_jugados / 900, 1.0)

score_tactico = sim × confianza

return {
    "score_tactico": score_tactico,
    "similitud": sim,
    "confianza": confianza,
    "fortalezas": [...],        # dims donde jugador ≥ necesidad
    "riesgos": [...],           # dims donde jugador no alcanza
    "necesidades_cubiertas": [...],
    "vector_jugador": [...],
    "vector_necesidad": [...],
}
```

---

### 7. SERVICIO DE SCOUTING (`services/scouting_service.py`)

#### `ScoutingService`

| Método | Descripción |
|--------|-------------|
| `buscar_jugadores_compatibles(club_id, perfil, limit, filtros)` | Pipeline completo de scouting |

#### Pipeline:

```
1. Obtener club + última temporada de BD
2. inferir_perfil(stats) → PerfilTacticoClub
3. DetectorNecesidades.detectar(perfil) → List[NecesidadTactica]
4. generar_vector_necesidad_club(perfil, necesidades) → vector 10d
5. Consultar jugadores históricos (JugadorRepository.listar)
6. Para cada jugador:
   a. orm_a_jugador(orm, ultima_temp) → dataclass Jugador
   b. compatibilidad_tactica(jugador, perfil, necesidades) → dict
7. Ordenar por score_tactico descendente
8. Retornar top N resultados
```

#### `ResultadoScouting` (dataclass)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `jugador` | Jugador | Dataclass del jugador |
| `score_compatibilidad` | float | Score final 0-1 |
| `score_tactico` | float | Score táctico 0-1 |
| `score_contextual` | float | Contexto (reservado) |
| `confianza_estadistica` | float | min(minutos/900, 1) |
| `fortalezas_detectadas` | List[str] | Dims donde destaca |
| `riesgos_detectados` | List[str] | Dims donde no alcanza |
| `necesidades_cubiertas` | List[str] | Roles que cubre |

---

### 8. SERVICIO DE CLUBES (`services/club_service.py`)

| Método | Descripción |
|--------|-------------|
| `crear_club(datos_base)` | Crea registro en clubes |
| `obtener_club(id)` | Obtiene club por ID |
| `listar_clubes(offset, limit)` | Lista paginada |
| `actualizar_club(id, datos)` | Actualiza campos |
| `eliminar_club(id)` | Elimina (cascade a temporadas) |
| `buscar_por_nombre(nombre)` | Búsqueda parcial |
| `agregar_temporada(club_id, stats)` | Agrega temporada con estadísticas |
| `obtener_temporadas(club_id)` | Historial de temporadas |
| `obtener_ultima_temporada(club_id)` | Última temporada |

---

### 9. ARQUITECTURA COMPLETA POR CAPAS

```
┌──────────────────────────────────────────────────────────────┐
│                    EJECUCIÓN                                  │
│  main.py / webapp.py / demo_persistencia.py                  │
│  demo_scouting_automatico.py                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              SERVICES (capa de negocio)                       │
│  JugadorService / TemporadaService                           │
│  ClubService / ScoutingService                                │
│  - orquesta repositorios + módulos tácticos                  │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│            REPOSITORIES (capa de datos)                       │
│  JugadorRepository / TemporadaRepository                     │
│  ClubRepository / TemporadaClubRepository                     │
│  - CRUD contra ORM                                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│          ORM MODELS (SQLAlchemy)                              │
│  JugadorORM 1──N TemporadaORM                                │
│  ClubORM     1──N TemporadaClubORM                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              CONNECTION (singleton)                           │
│  DatabaseManager → .env → engine → sessionmaker               │
└──────────────────────────────────────────────────────────────┘

MÓDULOS TÁCTICOS (transversales):
  inferencia_tactica.py → PerfilTacticoClub, inferir_perfil()
  detector_necesidades.py → NecesidadTactica, DetectorNecesidades
  vectorizacion.py → vectores 10d, similitud coseno, compatibilidad_tactica()
```

---

### 10. CORRECCIONES MATEMÁTICAS (v1.1)

| ID | Archivo | Problema | Solución |
|----|---------|----------|----------|
| #1 | config.py | Pesos sumaban 1.10 | Redistribuidos a 1.00 |
| #2 | calculadora.py | perfil_jugador: pct²/100 | Cambiado a pct directo |
| #3 | calculadora.py | modelo_juego: sj/10 → [0.1,1] | Cambiado a (sj-1)/9 → [0,1] |
| #4 | fisico.py | score_carga saltaba 5→10 en 70% | Rampa lineal 60-70% |

---

### 11. COMANDOS DE EJECUCIÓN

```powershell
# Instalar dependencias
pip install -r requirements.txt

# Configurar BD
copy .env.example .env
python -m mpsc.database.init_db

# Demos
python examples/demo_persistencia.py          # CRUD jugadores (v1.1)
python examples/demo_scouting_automatico.py    # Scouting masivo (v2.0)

# Sistema original (sin BD)
python mpsc/main.py                            # CLI interactiva
python mpsc/webapp.py                          # Web http://localhost:8765

# Migraciones Alembic
alembic upgrade head
```

---

### 12. OUTPUT DE DEMO v2.0 (verificado)

```
PERFIL TACTICO DEL CLUB:
  amplitud               ████████░░ 8.0
  verticalidad           ██████░░░░ 6.6
  posesion               ████████░░ 8.8
  intensidad_presion     ████████░░ 8.5
  control_juego          █████████░ 9.1

RANKING DE JUGADORES COMPATIBLES (top 5):
  1  Carlos López      mediocampista_central    0.918  confianza 1.000
  2  Edson Álvarez     mediocampista_defensivo  0.753  confianza 1.000
  3  Santi Giménez     delantero_centro         0.737  confianza 1.000
  4  Luis Chávez       mediocampista_central    0.707  confianza 1.000
  5  Julián Quiñones   delantero_centro         0.687  confianza 1.000
```

---

### 13. FASE 2 COMPLETA — CHECKLIST

- [x] CRUD Clubes (ORM, repositorio, servicio, migración)
- [x] Perfil Táctico Automático (12 dimensiones, fórmulas heurísticas)
- [x] Detección de Necesidades (7 reglas extensibles)
- [x] Vectorización de Jugadores (10 dimensiones 0-1)
- [x] Vector de Necesidad del Club
- [x] Similitud Coseno + Compatibilidad Táctica
- [x] Motor de Búsqueda Masiva (ScoutingService)
- [x] Demo funcional verificado
- [x] Sin modificar nada del sistema original
- [x] Preparado para futuras fases ML
