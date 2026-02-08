"""
KNA History Web Application - Application Factory

Slim factory that creates and configures the Flask application.
All routes are in blueprints for clean separation of concerns.

Architecture:
- Configuration: Single config instance (DRY)
- Services: Single reader/loader instances (efficient)
- Routes: All in blueprints (organized)
- Tests: Easy to mock and test
"""

import os

from flask import Flask
from flask_login import LoginManager

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.data_entry import data_entry_bp
from blueprints.public import public_bp
from kna_data import (
    KnaDataLoader,
    KnaDataReader,
    User,
    db,
    get_config,
    init_databases,
)
from logging_kna import logger


def create_app(env: str = None) -> Flask:
    """
    Application factory - creates and configures Flask app.

    Follows the application factory pattern for:
    - Testability (can create multiple apps with different configs)
    - Flexibility (can pass different environments)
    - Clean separation (all routes in blueprints)

    Args:
        env: Environment ('development', 'production', 'testing')
             If None, uses FLASK_ENV environment variable

    Returns:
        Configured Flask application ready to run

    Example:
        >>> app = create_app('development')
        >>> app.run(debug=True)
    """
    app = Flask(__name__)

    # Step 1: Load configuration (ONCE)
    config = get_config(env)
    app.config.from_object(config)
    app.config["KNA_CONFIG"] = config

    _log_startup_info(config)

    # Step 2: Initialize databases (ONCE)
    init_databases(app, config)

    # Step 3: Initialize KNA services (ONCE)
    _init_kna_services(app, config)

    # Step 4: Setup authentication
    _init_authentication(app)

    # Step 5: Register all blueprints
    _register_blueprints(app)

    # Step 6: Create default admin user
    _create_default_admin(app)

    logger.info("✓ Application initialization complete")
    return app


def _log_startup_info(config):
    """Log application startup information"""
    logger.info("=" * 60)
    logger.info("Starting KNA History Archive")
    logger.info(f"Environment: {config.__class__.__name__}")
    logger.info(f"Debug: {config.DEBUG}")
    logger.info(f"KNA DB: {config.SQLITE_KNA_PATH}")
    logger.info(f"Users DB: {config.SQLITE_USERS_PATH}")
    logger.info(f"Resources: {config.DIR_RESOURCES}")
    logger.info("=" * 60)


def _init_kna_services(app: Flask, config):
    """
    Initialize KNA data services and store in app context.

    Services are created ONCE and shared across all requests.
    Blueprints access them via current_app.config.

    Args:
        app: Flask application
        config: Configuration object

    Raises:
        Exception: If services cannot be initialized
    """
    try:
        # Create reader ONCE
        reader = KnaDataReader(config=config)
        app.config["KNA_READER"] = reader
        logger.info("✓ KNA Reader initialized")

        # Create loader ONCE
        loader = KnaDataLoader(config=config)
        app.config["KNA_LOADER"] = loader
        logger.info("✓ KNA Loader initialized")

    except Exception as e:
        logger.error(f"Failed to initialize KNA services: {e}")
        # Store None so blueprints can handle gracefully
        app.config["KNA_READER"] = None
        app.config["KNA_LOADER"] = None
        raise


def _init_authentication(app: Flask):
    """
    Initialize Flask-Login for user authentication.

    Args:
        app: Flask application
    """
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Log in om deze pagina te bekijken."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.init_app(app)
    logger.info("✓ Authentication initialized")


def _register_blueprints(app: Flask):
    """
    Register all application blueprints.

    Blueprint organization:
    - public: Public-facing routes (home, about, content browsing)
    - auth: Authentication (login, logout)
    - admin: Admin panel (Excel upload, user management)
    - data_entry: Interactive data entry (add/edit members, performances)

    Args:
        app: Flask application
    """
    # Public routes (no prefix - at root level)
    app.register_blueprint(public_bp)

    # Authentication routes
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Admin routes
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Data entry routes
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")

    logger.info("✓ Blueprints registered")


def _create_default_admin(app: Flask):
    """
    Create default admin user if none exists.

    Creates an admin user with credentials from environment variables
    or defaults to admin/admin2026!

    Args:
        app: Flask application
    """
    with app.app_context():
        try:
            if not User.query.filter_by(role="admin").first():
                admin_password = os.getenv("ADMIN_PASSWORD", "admin2026!")

                admin = User(
                    username="admin",
                    email="admin@kna-hillegom.local",
                    role="admin"
                )
                admin.set_password(admin_password)

                db.session.add(admin)
                db.session.commit()

                logger.info("✓ Created default admin user")
                if app.config["DEBUG"]:
                    logger.warning(f"Admin password: {admin_password}")
            else:
                logger.info("✓ Admin user exists")
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")


if __name__ == "__main__":
    """Development server - use gunicorn in production"""
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", False)
    )
