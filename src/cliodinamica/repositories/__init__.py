"""Persistencia de resultados (patrón Repository)."""

from .base import Repository
from .csv_repo import CsvRepository
from .sqlite_repo import SqliteRepository

__all__ = ["CsvRepository", "Repository", "SqliteRepository"]
