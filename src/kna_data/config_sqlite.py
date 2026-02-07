"""
KNA Data Package - Unified Configuration

Centralized configuration for database connections, Flask settings, and paths.
Supports MariaDB, SQLite, and local development environments.
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
    
    # Database type selection
    # Set DB_TYPE=mariadb to use MariaDB, otherwise uses SQLite (default)
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
    
    # MariaDB configuration (only used if DB_TYPE=mariadb)
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    MARIADB_USER = os.getenv("MARIADB_USER", "root")
    MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "kna-toneel")
    MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "kna")
    
    # SQLite configuration (default)
    SQLITE_PATH = os.getenv("SQLITE_PATH", "kna_history.db")
    
    # Resources directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "/data/resources/")
    
    @property
    def mariadb_url(self) -> str:
        """Get SQLAlchemy database URL for MariaDB (KNA data)"""
        return f"mysql+mysqldb://{self.MARIADB_USER}:{self.MARIADB_PASSWORD}@{self.MARIADB_HOST}/{self.MARIADB_DATABASE}"
    
    @property
    def sqlite_url(self) -> str:
        """Get SQLAlchemy database URL for SQLite (KNA data)"""
        return f"sqlite:///{self.SQLITE_PATH}"
    
    @property
    def kna_database_url(self) -> str:
        """Get the appropriate database URL based on DB_TYPE setting"""
        if self.DB_TYPE == "mariadb":
            return self.mariadb_url
        else:
            return self.sqlite_url
    
    def get_engine(self):
        """Get SQLAlchemy engine for KNA data (SQLite or MariaDB based on config)"""
        return create_engine(self.kna_database_url)
    
    @property
    def dir_resources(self) -> str:
        """Get resources directory path"""
        return self.DIR_RESOURCES


class DevelopmentConfig(Config):
    """Development configuration (local SQLite database by default)"""
    
    DEBUG = True
    
    # KNA data: Use SQLite by default in development
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    SQLITE_PATH = os.getenv("SQLITE_PATH", "kna_dev.db")
    
    # Override to use MariaDB in development if needed
    MARIADB_HOST = "127.0.0.1:3306"
    
    # Flask-Login users database (SQLite for development)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "sqlite:///users_dev.db"
    )


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    
    # KNA data: Use SQLite by default, set DB_TYPE=mariadb to use MariaDB
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    SQLITE_PATH = os.getenv("SQLITE_PATH", "/data/kna_history.db")
    
    # MariaDB settings (only used if DB_TYPE=mariadb)
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    
    # Flask-Login users database
    # Use SQLite by default for user management too
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///users_prod.db"
    )
    
    # Alternative: Use MariaDB for user management (if DB_TYPE=mariadb)
    # Uncomment this to use MariaDB for users when using MariaDB for KNA data
    # if os.getenv("DB_TYPE", "sqlite") == "mariadb":
    #     SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://{Config.MARIADB_USER}:{Config.MARIADB_PASSWORD}@{os.getenv('MARIADB_HOST', 'mariadb')}/kna_users"


class TestingConfig(Config):
    """Testing configuration (always uses in-memory SQLite)"""
    
    TESTING = True
    DB_TYPE = "sqlite"
    SQLITE_PATH = ":memory:"
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
    
    Examples:
        # Use SQLite (default):
        config = get_config('production')
        
        # Use MariaDB (set environment variable):
        os.environ['DB_TYPE'] = 'mariadb'
        config = get_config('production')
    """
    if env is None:
        env = os.getenv("FLASK_ENV") or os.getenv("KNA_ENV", "production")
    
    return config.get(env, config["default"])()


# Convenience methods for backwards compatibility
Config.for_production = lambda: get_config("production")
Config.for_development = lambda: get_config("development")
Config.for_testing = lambda: get_config("testing")
