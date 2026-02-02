"""
KNA Data Package - Configuration

Centralized configuration for database connections and paths.
"""
import os
from sqlalchemy import create_engine
from typing import Optional


class Config:
    """Configuration for KNA database and resources"""
    
    def __init__(
        self,
        db_host: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        db_name: Optional[str] = None,
        dir_resources: Optional[str] = None,
    ):
        # Database configuration
        self.db_host = db_host or os.getenv("MARIADB_HOST", "mariadb")
        self.db_user = db_user or os.getenv("MARIADB_USER", "root")
        self.db_password = db_password or os.getenv("MARIADB_PASSWORD", "kna-toneel")
        self.db_name = db_name or os.getenv("MARIADB_DATABASE", "kna")
        
        # Resources directory
        self.dir_resources = dir_resources or os.getenv("DIR_RESOURCES", "/data/resources/")
        
    @property
    def db_url(self) -> str:
        """Get SQLAlchemy database URL"""
        return f"mysql+mysqldb://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        return create_engine(self.db_url)
    
    @classmethod
    def for_development(cls):
        """Development configuration (local database)"""
        return cls(db_host="127.0.0.1:3306")
    
    @classmethod
    def for_production(cls):
        """Production configuration (container database)"""
        return cls(db_host="mariadb")
