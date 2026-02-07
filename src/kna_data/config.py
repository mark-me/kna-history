"""
KNA Data Package - SQLite Configuration

Centralized configuration for database connections, Flask settings, and paths.
Uses SQLite for both KNA data and user authentication.
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
    
    # SQLite configuration for KNA data
    SQLITE_PATH = os.getenv("SQLITE_PATH", "kna_history.db")
    
    # Resources directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "/data/resources/")
    
    @property
    def sqlite_url(self) -> str:
        """Get SQLAlchemy database URL for SQLite (KNA data)"""
        return f"sqlite:///{self.SQLITE_PATH}"
    
    def get_engine(self):
        """Get SQLAlchemy engine for KNA data (SQLite)"""
        return create_engine(self.sqlite_url)
    
    @property
    def dir_resources(self) -> str:
        """Get resources directory path"""
        return self.DIR_RESOURCES


class DevelopmentConfig(Config):
    """Development configuration (local SQLite database)"""
    
    DEBUG = True
    
    # KNA data: SQLite in current directory
    SQLITE_PATH = os.getenv("SQLITE_PATH", "kna_dev.db")
    
    # Flask-Login users database (SQLite)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "sqlite:///users_dev.db"
    )
    
    # Resources in local directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "./resources/")


class ProductionConfig(Config):
    """Production configuration (SQLite in data directory)"""
    
    DEBUG = False
    
    # KNA data: SQLite in /data directory
    SQLITE_PATH = os.getenv("SQLITE_PATH", "/data/kna_history.db")
    
    # Flask-Login users database (SQLite)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:////data/users_prod.db"
    )
    
    # Resources in /data directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "/data/resources/")


class TestingConfig(Config):
    """Testing configuration (in-memory SQLite)"""
    
    TESTING = True
    
    # Both databases in memory for testing
    SQLITE_PATH = ":memory:"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    # Temporary resources directory
    DIR_RESOURCES = "/tmp/kna_resources/"


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
    
    Examples:
        # Development (uses kna_dev.db and users_dev.db):
        config = get_config('development')
        
        # Production (uses /data/kna_history.db and /data/users_prod.db):
        config = get_config('production')
        
        # Testing (uses in-memory databases):
        config = get_config('testing')
    """
    if env is None:
        env = os.getenv("FLASK_ENV") or os.getenv("KNA_ENV", "production")
    
    return config.get(env, config["default"])()


# Convenience methods for backwards compatibility
Config.for_production = lambda: get_config("production")
Config.for_development = lambda: get_config("development")
Config.for_testing = lambda: get_config("testing")
