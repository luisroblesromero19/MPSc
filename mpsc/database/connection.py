"""
MPSc — database/connection.py
Gestión de conexión MySQL vía SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    _engine = None
    _SessionLocal = None

    @classmethod
    def get_database_url(cls) -> str:
        user = os.getenv("MPSc_DB_USER", "root")
        password = os.getenv("MPSc_DB_PASSWORD", "")
        host = os.getenv("MPSc_DB_HOST", "localhost")
        port = os.getenv("MPSc_DB_PORT", "3306")
        name = os.getenv("MPSc_DB_NAME", "mpsc_scouting")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    @classmethod
    def initialize(cls, database_url: str = None, echo: bool = False):
        if database_url is None:
            database_url = cls.get_database_url()
        cls._engine = create_engine(database_url, echo=echo, pool_pre_ping=True)
        cls._SessionLocal = sessionmaker(bind=cls._engine, autocommit=False, autoflush=False)

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls.initialize()
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        if cls._SessionLocal is None:
            cls.initialize()
        return cls._SessionLocal

    @classmethod
    def dispose(cls):
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._SessionLocal = None


def get_session():
    factory = DatabaseManager.get_session_factory()
    session = factory()
    try:
        return session
    except:
        session.close()
        raise


def init_db():
    from .models.jugador_model import JugadorORM
    from .models.temporada_model import TemporadaORM
    from .models.club_model import ClubORM
    from .models.temporada_club_model import TemporadaClubORM
    Base.metadata.create_all(bind=DatabaseManager.get_engine())
