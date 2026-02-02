"""
KNA Data Package

A package for managing KNA theatre group historical data:
- Reading data from the database
- Loading data from Excel files
- Validating data integrity
"""

from .config import Config
from .reader import KnaDataReader
from .loader import KnaDataLoader

__version__ = "1.0.0"

__all__ = [
    "Config",
    "KnaDataReader",
    "KnaDataLoader",
]
