"""
MPSc — database/migrations/env.py
Configuración de entorno para Alembic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv
import os

from mpsc.database.connection import Base

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = (
    f"mysql+pymysql://{os.getenv('MPSc_DB_USER', 'root')}:"
    f"{os.getenv('MPSc_DB_PASSWORD', '')}@"
    f"{os.getenv('MPSc_DB_HOST', 'localhost')}:"
    f"{os.getenv('MPSc_DB_PORT', '3306')}/"
    f"{os.getenv('MPSc_DB_NAME', 'mpsc_scouting')}"
)
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
