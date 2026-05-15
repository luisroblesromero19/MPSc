"""
MPSc — database/migrations/versions/0002_clubes.py
Migración: tablas clubes y temporadas_club.
"""

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON


def upgrade():
    op.create_table(
        "clubes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False, index=True),
        sa.Column("pais", sa.String(100), server_default=""),
        sa.Column("liga", sa.String(50), server_default="", index=True),
        sa.Column("division", sa.String(50), server_default=""),
        sa.Column("temporada_actual", sa.String(20), server_default=""),
        sa.Column("entrenador", sa.String(255), server_default=""),
        sa.Column("sistema_tactico", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "temporadas_club",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False, index=True),
        sa.Column("temporada", sa.String(20), server_default="", index=True),
        sa.Column("partidos", sa.Integer(), server_default="0"),
        sa.Column("goles_favor", sa.Integer(), server_default="0"),
        sa.Column("goles_contra", sa.Integer(), server_default="0"),
        sa.Column("asistencias", sa.Integer(), server_default="0"),
        sa.Column("posesion", sa.Float(), server_default="0"),
        sa.Column("pases_precisos", sa.Integer(), server_default="0"),
        sa.Column("precision_pases", sa.Float(), server_default="0"),
        sa.Column("balones_largos", sa.Integer(), server_default="0"),
        sa.Column("precision_balones_largos", sa.Float(), server_default="0"),
        sa.Column("centros", sa.Integer(), server_default="0"),
        sa.Column("precision_centros", sa.Float(), server_default="0"),
        sa.Column("regates", sa.Integer(), server_default="0"),
        sa.Column("corners", sa.Integer(), server_default="0"),
        sa.Column("tiros", sa.Integer(), server_default="0"),
        sa.Column("tiros_puerta", sa.Integer(), server_default="0"),
        sa.Column("porterias_cero", sa.Integer(), server_default="0"),
        sa.Column("intercepciones", sa.Integer(), server_default="0"),
        sa.Column("recuperaciones", sa.Integer(), server_default="0"),
        sa.Column("errores_tiro", sa.Integer(), server_default="0"),
        sa.Column("duelos_ganados", sa.Integer(), server_default="0"),
        sa.Column("duelos_aereos", sa.Integer(), server_default="0"),
        sa.Column("fueras_juego", sa.Integer(), server_default="0"),
        sa.Column("faltas", sa.Integer(), server_default="0"),
        sa.Column("amarillas", sa.Integer(), server_default="0"),
        sa.Column("rojas", sa.Integer(), server_default="0"),
        sa.Column("sofascore_raw", JSON, nullable=True),
        sa.Column("metricas_ofensivas_json", JSON, nullable=True),
        sa.Column("metricas_defensivas_json", JSON, nullable=True),
        sa.Column("metricas_transicion_json", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["club_id"], ["clubes.id"], ondelete="CASCADE"),
    )


def downgrade():
    op.drop_table("temporadas_club")
    op.drop_table("clubes")
