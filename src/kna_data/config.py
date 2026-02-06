"""
KNA Data Package - Unified Configuration

Centralized configuration for database connections, Flask settings, and paths.
Supports both Docker and local development environments.
"""
import os
from sqlalchemy import create_engine


class Config:
    """Base configuration for KNA application"""

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MiB
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration (MariaDB for data)
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    MARIADB_USER = os.getenv("MARIADB_USER", "root")
    MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "kna-toneel")
    MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "kna")
    
    # Resources directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "/data/resources/")
    
    @property
    def mariadb_url(self) -> str:
        """Get SQLAlchemy database URL for MariaDB (KNA data)"""
        return f"mysql+mysqldb://{self.MARIADB_USER}:{self.MARIADB_PASSWORD}@{self.MARIADB_HOST}/{self.MARIADB_DATABASE}"
    
    def get_engine(self):
        """Get SQLAlchemy engine for MariaDB (KNA data)"""
        return create_engine(self.mariadb_url)
    
    @property
    def dir_resources(self) -> str:
        """Get resources directory path"""
        return self.DIR_RESOURCES


class DevelopmentConfig(Config):
    """Development configuration (local database)"""
    
    DEBUG = True
    MARIADB_HOST = "127.0.0.1:3306"
    
    # Flask-Login users database (SQLite for development)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "sqlite:///dev.db"
    )


class ProductionConfig(Config):
    """Production configuration (Docker container database)"""
    
    DEBUG = False
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    
    # Flask-Login users database (can be same MariaDB or separate)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+mysqldb://{Config.MARIADB_USER}:{Config.MARIADB_PASSWORD}@{os.getenv('MARIADB_HOST', 'mariadb')}/kna_users"
    )


class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    MARIADB_HOST = "127.0.0.1:3306"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Configuration dictionary for easy access
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": ProductionConfig
}


def get_config(env: str = None) -> Config:
    """
    Get configuration object based on environment.
    
    Args:
        env: Environment name ('development', 'production', 'testing')
             If None, uses FLASK_ENV or KNA_ENV environment variable
    
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv("FLASK_ENV") or os.getenv("KNA_ENV", "production")
    
    return config.get(env, config["default"])()
