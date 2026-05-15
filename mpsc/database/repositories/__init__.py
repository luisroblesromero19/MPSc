"""
MPSc — database/repositories
"""

from .jugador_repository import JugadorRepository
from .temporada_repository import TemporadaRepository
from .club_repository import ClubRepository
from .temporada_club_repository import TemporadaClubRepository

__all__ = [
    "JugadorRepository", "TemporadaRepository",
    "ClubRepository", "TemporadaClubRepository",
]
