"""
MPSc — database/init_db.py
Script para crear/actualizar la base de datos y tablas.
Uso: python -m mpsc.database.init_db
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
from mpsc.database.connection import DatabaseManager, Base, init_db


def main():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        example_path = Path(__file__).resolve().parent.parent.parent / ".env.example"
        if example_path.exists():
            print("⚠  No se encontró .env. Copia .env.example como .env y configura las credenciales.")
            load_dotenv(example_path)

    db_url = DatabaseManager.get_database_url()
    print(f"🔌 Conectando a: {db_url}")

    DatabaseManager.initialize(db_url, echo=False)
    init_db()
    print("✓ Tablas creadas/verificadas correctamente.")
    DatabaseManager.dispose()


if __name__ == "__main__":
    main()
