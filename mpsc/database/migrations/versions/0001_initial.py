"""
MPSc — mpsc/database/migrations/versions/0001_initial.py
Migración inicial: tablas jugadores y temporadas_jugador.
"""

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON


def upgrade():
    op.create_table(
        "jugadores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False, index=True),
        sa.Column("fecha_nacimiento", sa.String(10), server_default=""),
        sa.Column("edad", sa.Integer(), server_default="0"),
        sa.Column("pais_origen", sa.String(100), server_default=""),
        sa.Column("ciudad_actual", sa.String(255), server_default=""),
        sa.Column("idioma", sa.String(100), server_default=""),
        sa.Column("experiencia_extranjero", sa.Boolean(), server_default="0"),
        sa.Column("valor_mercado", sa.String(100), server_default=""),
        sa.Column("posicion_principal", sa.String(50), server_default="", index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "temporadas_jugador",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("jugador_id", sa.Integer(), nullable=False, index=True),
        sa.Column("temporada", sa.String(20), server_default="", index=True),
        sa.Column("club_actual", sa.String(255), server_default=""),
        sa.Column("liga", sa.String(50), server_default=""),
        sa.Column("posicion_tabla", sa.Integer(), server_default="0"),
        sa.Column("total_equipos_liga", sa.Integer(), server_default="0"),
        sa.Column("tiene_copa", sa.Boolean(), server_default="0"),
        sa.Column("tiene_internacional", sa.Boolean(), server_default="0"),
        sa.Column("sistema_tactico_club", sa.String(100), server_default=""),
        sa.Column("estilo_ofensivo", sa.String(100), server_default=""),
        sa.Column("estilo_defensivo", sa.String(100), server_default=""),
        sa.Column("estilo_transicion", sa.String(100), server_default=""),
        sa.Column("altitud_ciudad", sa.Float(), server_default="0"),
        sa.Column("minutos_jugados", sa.Float(), server_default="0"),
        sa.Column("minutos_posibles", sa.Float(), server_default="0"),
        sa.Column("posicion", sa.String(50), server_default="", index=True),
        sa.Column("rol", sa.String(50), server_default=""),
        sa.Column("estadisticas_json", JSON, nullable=True),
        sa.Column("num_lesiones", sa.Integer(), server_default="0"),
        sa.Column("tipo_lesion", sa.String(50), server_default=""),
        sa.Column("semanas_baja_promedio", sa.Float(), server_default="0"),
        sa.Column("zonas_json", JSON, nullable=True),
        sa.Column("sofascore_jugador_raw", sa.Text(), server_default=""),
        sa.Column("stats_club_origen_raw", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["jugador_id"], ["jugadores.id"], ondelete="CASCADE"),
    )


def downgrade():
    op.drop_table("temporadas_jugador")
    op.drop_table("jugadores")
