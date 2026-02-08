"""
KNA History Web Application

Clean architecture with separated concerns:
- Configuration: Environment-based config
- Databases: Users (Flask-SQLAlchemy) + KNA Content (pandas/SQLAlchemy Core)
- Authentication: Flask-Login with User model
- Blueprints: Admin, Auth, Data Entry
"""

import os

from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, login_required

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.data_entry import data_entry_bp
from blueprints.helpers import with_kna_reader
from kna_data import (
    DatabaseManager,
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
    Create and configure Flask application.

    Centralizes all initialization - config, database, services created ONCE.

    Args:
        env: Environment ('development', 'production', 'testing')
             If None, uses FLASK_ENV environment variable

    Returns:
        Configured Flask application with services ready
    """
    app = Flask(__name__)

    # Step 1: Configuration
    config = get_config(env)
    app.config.from_object(config)

    # Store config object for blueprints to access
    app.config["KNA_CONFIG"] = config

    logger.info("=" * 60)
    logger.info("Starting KNA History Archive")
    logger.info(f"Environment: {config.__class__.__name__}")
    logger.info(f"Debug: {config.DEBUG}")
    logger.info(f"KNA DB: {config.SQLITE_KNA_PATH}")
    logger.info(f"Users DB: {config.SQLITE_USERS_PATH}")
    logger.info("=" * 60)

    # Step 2: Database Initialization
    init_databases(app, config)

    # Step 3: Initialize KNA Services
    _init_kna_services(app, config)

    # Step 4: Authentication
    _init_authentication(app)

    # Step 5: Register Blueprints
    _register_blueprints(app)

    # Step 6: Register Routes
    _register_public_routes(app)
    _register_health_routes(app)

    # Step 7: Create Default Admin
    _create_default_admin(app)

    logger.info("Application initialization complete")
    return app


def _init_kna_services(app: Flask, config):
    """
    Initialize KNA data services ONCE and store in app context.

    All routes will access these shared instances via current_app.config
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
    """Initialize Flask-Login"""
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
    """Register all blueprints"""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")
    logger.info("✓ Blueprints registered")


def _register_public_routes(app: Flask):
    """
    Register public-facing routes.

    Uses blueprints.helpers to access services (DRY pattern)
    """
    # Optional login requirement
    require_login = os.getenv("REQUIRE_LOGIN", "false").lower() == "true"

    def optional_login(f):
        return login_required(f) if require_login else f

    @app.route("/")
    @app.route("/home")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html", title="Over")

    @app.route("/cdn/<path:filepath>")
    @optional_login
    @with_kna_reader
    def cdn(reader, filepath):
        """Serve media files (reader injected by decorator)"""
        try:
            dir_path, filename = os.path.split(reader.decode(filepath))
            return send_from_directory(dir_path, filename, as_attachment=False)
        except Exception as e:
            logger.error(f"CDN error: {e}")
            return "File not found", 404

    @app.route("/image/<path_image>")
    @optional_login
    @with_kna_reader
    def show_image(reader, path_image: str):
        """Display image (reader injected)"""
        try:
            image_data = reader.medium(path=path_image)
            return render_template("image.html", image=image_data)
        except Exception as e:
            logger.error(f"Image error: {e}")
            return _render_error("Afbeelding niet gevonden"), 404

    @app.route("/pdf/<path_pdf>")
    @optional_login
    def show_document(path_pdf: str):
        """Display PDF document"""
        return render_template("pdf.html", file_pdf=path_pdf)

    @app.route("/video/<path_video>")
    @optional_login
    @with_kna_reader
    def show_movie(reader, path_video: str):
        """Display video (reader injected)"""
        try:
            video_data = reader.medium(path=path_video)
            return render_template("video.html", video=video_data)
        except Exception as e:
            logger.error(f"Video error: {e}")
            return _render_error("Video niet gevonden"), 404

    @app.route("/leden")
    @optional_login
    @with_kna_reader
    def view_leden(reader):
        """View members list (reader injected)"""
        leden = reader.leden()
        return render_template("leden.html", leden=leden)

    @app.route("/voorstellingen")
    @optional_login
    @with_kna_reader
    def view_voorstellingen(reader):
        """View performances list (reader injected)"""
        voorstellingen = reader.voorstellingen()
        return render_template("voorstellingen.html", voorstellingen=voorstellingen)

    @app.route("/tijdslijn")
    @optional_login
    @with_kna_reader
    def view_tijdslijn(reader):
        """View timeline (reader injected)"""
        tijdslijn = reader.timeline()
        return render_template("tijdslijn.html", tijdslijn=tijdslijn)

    @app.route("/lid_media/<lid>")
    @optional_login
    @with_kna_reader
    def lid_media(reader, lid: str):
        """View member media (reader injected)"""
        media = reader.lid_media(id_lid=lid)
        lid_info = reader.lid_info(id_lid=lid)
        return render_template("lid_media.html", lid=lid_info, media=media)

    @app.route("/voorstelling_media/<voorstelling>")
    @optional_login
    @with_kna_reader
    def voorstelling_media(reader, voorstelling: str):
        """View performance media (reader injected)"""
        info = reader.voorstelling_info(voorstelling=voorstelling)
        media = reader.voorstelling_media(voorstelling=voorstelling)
        return render_template(
            "voorstelling_media.html", voorstelling=info, media=media
        )

    @app.route("/voorstelling_lid_media/<voorstelling>/<lid>")
    @optional_login
    @with_kna_reader
    def voorstelling_lid_media(reader, voorstelling: str, lid: str):
        """View member media in performance (reader injected)"""
        info = reader.voorstelling_info(voorstelling=voorstelling)
        media = reader.voorstelling_lid_media(voorstelling=voorstelling, lid=lid)
        return render_template(
            "voorstelling_media.html", voorstelling=info, media=media
        )


def _register_health_routes(app: Flask):
    """Register health check and monitoring routes"""

    @app.route("/health")
    def health():
        """Comprehensive health check"""
        from blueprints.helpers import get_kna_config, get_kna_reader

        status = {
            "status": "healthy",
            "users_db": DatabaseManager.check_users_db_health(),
        }

        try:
            config = get_kna_config()
            kna_engine = config.get_kna_engine()
            status["kna_db"] = DatabaseManager.check_kna_db_health(kna_engine)
        except Exception as e:
            logger.error(f"KNA health check failed: {e}")
            status["kna_db"] = {"status": "not_initialized", "error": str(e)}

        # Overall status
        is_healthy = all(
            db_status.get("status") == "healthy"
            for db_status in [status["users_db"], status["kna_db"]]
        )
        status["status"] = "healthy" if is_healthy else "degraded"

        http_status = 200 if is_healthy else 503
        return status, http_status


def _create_default_admin(app: Flask):
    """Create default admin user if none exists"""
    with app.app_context():
        try:
            if not User.query.filter_by(role="admin").first():
                admin_password = os.getenv("ADMIN_PASSWORD", "admin2026!")

                admin = User(
                    username="admin", email="admin@kna-hillegom.local", role="admin"
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


def _render_error(message: str) -> str:
    """Render error template"""
    try:
        return render_template("error.html", message=message)
    except:
        return f"<h1>Error</h1><p>{message}</p>"


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
