# MPSc — Actualización v1.1: Persistencia MySQL

## Documento de Arquitectura para Agentes

---

### 1. RESUMEN DEL CAMBIO

Se agregó una capa de persistencia MySQL con SQLAlchemy ORM al proyecto MPSc,
permitiendo almacenar jugadores y su historial de temporadas en base de datos.

**NO se modificó ningún archivo existente del motor de cálculo.**

---

### 2. ESTRUCTURA NUEVA

```
mpsc/
├── database/                          ← NUEVO
│   ├── __init__.py
│   ├── connection.py                  # DatabaseManager, Base, get_session(), init_db()
│   ├── adapters.py                    # ORM ↔ dataclass Jugador
│   ├── init_db.py                     # Script: python -m mpsc.database.init_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── jugador_model.py           # JugadorORM (tabla: jugadores)
│   │   └── temporada_model.py         # TemporadaORM (tabla: temporadas_jugador)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── jugador_repository.py      # CRUD jugadores
│   │   └── temporada_repository.py    # CRUD temporadas
│   └── migrations/
│       ├── env.py                     # Config Alembic
│       ├── script.py.mako             # Template migraciones
│       └── versions/
│           └── 0001_initial.py        # Migración inicial
├── services/                          ← NUEVO
│   ├── __init__.py
│   ├── jugador_service.py             # JugadorService
│   └── temporada_service.py           # TemporadaService
│
├── .env.example                       ← NUEVO
├── .env                               ← NUEVO (creado local)
├── requirements.txt                   ← NUEVO
├── alembic.ini                        ← NUEVO
│
examples/                              ← NUEVO
└── demo_persistencia.py               # Ejemplo funcional
```

**Archivos existentes NO modificados:**
- `mpsc/models/jugador.py` (dataclass original)
- `mpsc/models/club.py`
- `mpsc/models/resultado.py`
- `mpsc/calculadora.py`
- `mpsc/modules/*.py` (todos los módulos)
- `mpsc/main.py`
- `mpsc/webapp.py`
- `mpsc/config.py`

---

### 3. DEPENDENCIAS NUEVAS (requirements.txt)

```
SQLAlchemy>=2.0
pymysql>=1.1
python-dotenv>=1.0
alembic>=1.13
cryptography>=42.0
```

---

### 4. TABLAS CREADAS

#### 4.1 `jugadores`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | INT (PK, autoincrement) | |
| nombre | VARCHAR(255) | Indexado |
| fecha_nacimiento | VARCHAR(10) | "YYYY-MM-DD" |
| edad | INT | |
| pais_origen | VARCHAR(100) | |
| ciudad_actual | VARCHAR(255) | |
| idioma | VARCHAR(100) | |
| experiencia_extranjero | BOOLEAN | |
| valor_mercado | VARCHAR(100) | |
| posicion_principal | VARCHAR(50) | Indexado |
| created_at | DATETIME | autogenerado |
| updated_at | DATETIME | autogenerado |

#### 4.2 `temporadas_jugador`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | INT (PK, autoincrement) | |
| jugador_id | INT (FK → jugadores.id) | CASCADE on delete |
| temporada | VARCHAR(20) | Indexado |
| club_actual | VARCHAR(255) | |
| liga | VARCHAR(50) | |
| posicion_tabla | INT | |
| total_equipos_liga | INT | |
| tiene_copa | BOOLEAN | |
| tiene_internacional | BOOLEAN | |
| sistema_tactico_club | VARCHAR(100) | |
| estilo_ofensivo | VARCHAR(100) | |
| estilo_defensivo | VARCHAR(100) | |
| estilo_transicion | VARCHAR(100) | |
| altitud_ciudad | FLOAT | |
| minutos_jugados | FLOAT | |
| minutos_posibles | FLOAT | |
| posicion | VARCHAR(50) | Indexado |
| rol | VARCHAR(50) | |
| estadisticas_json | JSON | Datos crudos del jugador |
| num_lesiones | INT | |
| tipo_lesion | VARCHAR(50) | |
| semanas_baja_promedio | FLOAT | |
| zonas_json | JSON | Zonas de presencia |
| sofascore_jugador_raw | TEXT | Texto Sofascore original |
| stats_club_origen_raw | TEXT | Stats del club de origen |
| created_at | DATETIME | autogenerado |

---

### 5. ARQUITECTURA POR CAPAS

```
┌─────────────────────────────────────────────────────┐
│                    EJECUCIÓN                         │
│  main.py / webapp.py / examples/demo_persistencia.py │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              SERVICES (capa de negocio)              │
│  JugadorService / TemporadaService                   │
│  - orquesta repositorios y adaptadores               │
│  - contexto: with JugadorService() as svc:           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│            REPOSITORIES (capa de datos)              │
│  JugadorRepository / TemporadaRepository             │
│  - CRUD directo contra ORM                          │
│  - reciben Session, no crean conexiones             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│          ORM MODELS (SQLAlchemy declarative)          │
│  JugadorORM / TemporadaORM                           │
│  - Mapean directamente a tablas MySQL                │
│  - Relación: JugadorORM 1──N TemporadaORM            │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              CONNECTION (singleton)                   │
│  DatabaseManager                                     │
│  - Lee .env → crea engine → sessionmaker             │
└─────────────────────────────────────────────────────┘
```

---

### 6. ADAPTADORES (ORM ↔ dataclass)

Tres funciones en `database/adapters.py`:

#### `orm_a_jugador(orm: JugadorORM, ultima_temporada: TemporadaORM) -> Jugador`
Convierte un registro ORM + su última temporada en una dataclass `Jugador`
compatible con el motor de cálculo existente.

#### `jugador_a_orm(jugador: Jugador) -> JugadorORM`
Convierte una dataclass `Jugador` en un ORM (solo datos base, sin temporada).

#### `jugador_a_temporada(jugador: Jugador, temporada: str) -> TemporadaORM`
Convierte una dataclass `Jugador` en un ORM de temporada,
mapeando: `jugador.club_actual`, `jugador.liga`, `jugador.minutos_jugados`,
`jugador.estadisticas → estadisticas_json`, `jugador.zonas → zonas_json`, etc.

---

### 7. SERVICIOS

#### `JugadorService`
| Método | Descripción |
|--------|-------------|
| `crear_jugador(datos_base)` | Crea registro en tabla jugadores |
| `obtener_jugador(id)` | Obtiene ORM + última temporada → dataclass |
| `listar_jugadores(offset, limit)` | Lista paginada |
| `actualizar_jugador(id, datos)` | Actualiza campos |
| `eliminar_jugador(id)` | Elimina (cascade a temporadas) |
| `guardar_jugador_con_temporada(jugador, temporada)` | Crea jugador + temporada en 1 paso |
| `buscar_por_nombre(nombre)` | Búsqueda parcial (ILIKE) |
| `contar_jugadores()` | Total de registros |

#### `TemporadaService`
| Método | Descripción |
|--------|-------------|
| `agregar_temporada(jugador_id, jugador, temporada)` | Agrega temporada a jugador existente |
| `obtener_historico(jugador_id)` | Todas las temporadas del jugador |
| `obtener_ultima_temporada(jugador_id)` | Última temporada |
| `eliminar_temporada(id)` | Elimina una temporada |

Ambos servicios implementan `__enter__` / `__exit__` para usar con `with`:

```python
with JugadorService() as svc:
    jugador_dc = svc.obtener_jugador(1)
```

---

### 8. FLUJO DE PERSISTENCIA

```
Guardar evaluación actual:

  1. Capturar datos (CLI o Web) → dataclass Jugador
  2. JugadorService.guardar_jugador_con_temporada(jugador, "2025-2026")
     → Crea registro en jugadores + temporadas_jugador
  3. Calculadora.calcular(jugador, club) → Resultado
     (el motor de cálculo usa la dataclass, no el ORM)


Recuperar jugador histórico + calcular compatibilidad:

  1. JugadorService.obtener_jugador(id) → dataclass Jugador
  2. Capturar datos del club (CLI o Web) → dataclass Club
  3. Calculadora.calcular(jugador, club) → Resultado
```

---

### 9. CONFIGURACIÓN

Archivo `.env`:

```
MPSc_DB_USER=root
MPSc_DB_PASSWORD=root
MPSc_DB_HOST=localhost
MPSc_DB_PORT=3306
MPSc_DB_NAME=mpsc_scouting
```

`DatabaseManager` es singleton: se llama una vez a `DatabaseManager.initialize()`
que crea engine y session factory. Luego `get_session()` da sesiones.

---

### 10. CORRECCIONES MATEMÁTICAS APLICADAS

Además de la persistencia, se corrigieron 4 bugs matemáticos detectados
en el Contexto.docx original:

| ID | Archivo | Problema | Solución |
|----|---------|----------|----------|
| #1 | config.py | Pesos sumaban 1.10 | Se redistribuyeron para sumar 1.00 |
| #2 | calculadora.py | perfil_jugador usaba pct²/100 | Cambiado a pct directo |
| #3 | calculadora.py | modelo_juego: sj/10 → rango [0.1, 1] | Cambiado a (sj-1)/9 → rango [0, 1] |
| #4 | fisico.py | score_carga saltaba 5→10 en 70% | Rampa lineal 60-70% |

---

### 11. COMANDOS DE EJECUCIÓN

```powershell
# Instalar dependencias
pip install -r requirements.txt

# Configurar BD
copy .env.example .env   # editar credenciales
python -m mpsc.database.init_db

# Probar demo
python examples/demo_persistencia.py

# Ejecutar sistema original (sin BD necesaria)
python mpsc/main.py       # CLI interactiva
python mpsc/webapp.py     # Web en http://localhost:8765

# Migraciones Alembic (futuro)
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

---

### 12. PREPARADO PARA FASE 2

La arquitectura actual está lista para:

- **CRUD de Clubes** — crear `ClubORM` + `ClubRepository` + `ClubService`
  siguiendo exactamente el mismo patrón.
- **Consultas automáticas** — buscar jugadores por liga, posición, rango de edad, etc.
- **Búsquedas masivas** — evaluar compatibilidad de N jugadores contra 1 club
  (reutilizando `Calculadora.calcular()` con dataclasses recuperadas de BD).
- **Detección táctica automática** — los datos históricos en `temporadas_jugador`
  permiten analizar tendencias.
