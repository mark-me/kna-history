"""
KNA Data Package - Hybrid Structure

Public API with minimal exports.
Internal organization in sub-packages.
"""

# Infrastructure
from .config import get_config
from .database import db, init_databases

# Domain models
from .models import User

# Application services
from .services import KnaDataLoader, KnaDataReader

# Public API
__all__ = [
    'get_config',
    'db',
    'init_databases',
    'User',
    'KnaDataLoader',
    'KnaDataReader',
]

__version__ = '2.0.0'