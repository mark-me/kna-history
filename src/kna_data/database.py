"""
KNA Database Module

Centralized database initialization and management.
Separates concerns between Users DB and KNA Content DB.

IMPORTANT: Ensures database directories exist before creating databases.
"""
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect
from logging import logger

# Flask-SQLAlchemy instance (for Users database)
db = SQLAlchemy()


class DatabaseManager:
    """
    Manages database initialization and health checks.

    Responsibilities:
    - Ensure database directories exist
    - Initialize Flask-SQLAlchemy (users DB)
    - Create tables if they don't exist
    - Provide health check utilities
    """

    @staticmethod
    def init_app(app, config):
        """
        Initialize databases with Flask app.

        Args:
            app: Flask application instance
            config: Configuration object with database settings
        """
        # CRITICAL: Ensure database directories exist FIRST
        DatabaseManager._ensure_database_directories(config)

        # Configure Flask-SQLAlchemy for users database
        app.config['SQLALCHEMY_DATABASE_URI'] = config.users_database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO

        # Initialize Flask-SQLAlchemy
        db.init_app(app)

        # Create tables in app context
        with app.app_context():
            DatabaseManager._create_users_tables()
            DatabaseManager._log_database_info(config)

    @staticmethod
    def _ensure_database_directories(config):
        """
        Ensure database directories exist before creating databases.

        This is CRITICAL - SQLite cannot create files in non-existent directories.

        Args:
            config: Configuration object with database paths
        """
        for db_path in [config.SQLITE_KNA_PATH, config.SQLITE_USERS_PATH]:
            if db_path and db_path != ":memory:":
                # Get parent directory
                db_file = Path(db_path)
                db_dir = db_file.parent

                # Create directory if it doesn't exist
                if not db_dir.exists():
                    logger.info(f"Creating database directory: {db_dir}")
                    db_dir.mkdir(parents=True, exist_ok=True)

                # Verify directory is writable
                if not db_dir.exists() or not db_dir.is_dir():
                    raise RuntimeError(
                        f"Database directory does not exist or is not a directory: {db_dir}"
                    )

                # Check write permissions
                test_file = db_dir / '.write_test'
                try:
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    raise RuntimeError(
                        f"Database directory is not writable: {db_dir}\n"
                        f"Error: {e}"
                    )

                logger.info(f"✓ Database directory ready: {db_dir}")

    @staticmethod
    def _create_users_tables():
        """Create users database tables if they don't exist"""
        try:
            db.create_all()
            logger.info("✓ Users database tables initialized")
        except Exception as e:
            logger.error(f"Failed to create users tables: {e}")
            raise

    @staticmethod
    def _log_database_info(config):
        """Log database configuration for debugging"""
        logger.info(f"Users DB: {config.SQLITE_USERS_PATH}")
        logger.info(f"KNA Content DB: {config.SQLITE_KNA_PATH}")
        logger.info(f"Resources: {config.DIR_RESOURCES}")

    @staticmethod
    def check_users_db_health() -> dict:
        """
        Check users database health.

        Returns:
            dict: Health status with connection info
        """
        try:
            # Try a simple query
            result = db.session.execute(text("SELECT 1")).scalar()
            return {
                "status": "healthy",
                "connected": True,
                "test_query": result == 1
            }
        except Exception as e:
            logger.error(f"Users DB health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }

    @staticmethod
    def check_kna_db_health(engine) -> dict:
        """
        Check KNA content database health.

        Args:
            engine: SQLAlchemy engine for KNA database

        Returns:
            dict: Health status with table info
        """
        try:
            with engine.connect() as conn:
                # Check connection
                conn.execute(text("SELECT 1"))

                # Get table list
                inspector = inspect(engine)
                tables = inspector.get_table_names()

                return {
                    "status": "healthy",
                    "connected": True,
                    "tables": tables,
                    "table_count": len(tables)
                }
        except Exception as e:
            logger.error(f"KNA DB health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }

    @staticmethod
    def get_table_counts(engine) -> dict:
        """
        Get row counts for all tables in KNA database.

        Args:
            engine: SQLAlchemy engine for KNA database

        Returns:
            dict: Table names mapped to row counts
        """
        counts = {}
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            with engine.connect() as conn:
                for table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = result.scalar()
        except Exception as e:
            logger.error(f"Failed to get table counts: {e}")

        return counts


def init_databases(app, config):
    """
    Convenience function to initialize all databases.

    Ensures directories exist before database initialization.

    Args:
        app: Flask application
        config: Configuration object
    """
    DatabaseManager.init_app(app, config)
