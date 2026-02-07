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
from kna_data import (
    get_config,
    init_databases,
    db,
    User,
    KnaDataReader,
    DatabaseManager,
)
from logging_kna import logger


def create_app(env: str = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        env: Environment ('development', 'production', 'testing')
             If None, uses FLASK_ENV environment variable

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config(env)
    app.config.from_object(config)

    logger.info("Starting KNA History Archive")
    logger.info(f"Environment: {config.__class__.__name__}")
    logger.info(f"Debug: {config.DEBUG}")

    # Initialize databases
    init_databases(app, config)

    # Initialize authentication
    _init_authentication(app)

    # Register blueprints
    _register_blueprints(app)

    # Initialize KNA data reader
    kna_reader = _init_kna_reader(config)

    # Register routes
    _register_public_routes(app, kna_reader, config)
    _register_health_routes(app, kna_reader, config)

    # Create default admin user
    _create_default_admin(app)

    return app


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
    logger.info("Authentication initialized")


def _register_blueprints(app: Flask):
    """Register all blueprints"""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")
    logger.info("Blueprints registered")


def _init_kna_reader(config) -> KnaDataReader | None:
    """Initialize KNA data reader"""
    try:
        reader = KnaDataReader(config=config)
        logger.info("KNA data reader initialized")
        return reader
    except Exception as e:
        logger.error(f"Failed to initialize KNA reader: {e}")
        return None


def _register_public_routes(app: Flask, kna_reader: KnaDataReader | None, config):
    """Register public-facing routes"""

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
    def cdn(filepath):
        """Serve media files"""
        if not kna_reader:
            return "Service unavailable", 503

        try:
            dir_path, filename = os.path.split(kna_reader.decode(filepath))
            return send_from_directory(dir_path, filename, as_attachment=False)
        except Exception as e:
            logger.error(f"CDN error: {e}")
            return "File not found", 404

    @app.route("/image/<path_image>")
    @optional_login
    def show_image(path_image: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            image_data = kna_reader.medium(path=path_image)
            return render_template("image.html", image=image_data)
        except Exception as e:
            logger.error(f"Image error: {e}")
            return _render_error("Afbeelding niet gevonden"), 404

    @app.route("/pdf/<path_pdf>")
    @optional_login
    def show_document(path_pdf: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        return render_template("pdf.html", file_pdf=path_pdf)

    @app.route("/video/<path_video>")
    @optional_login
    def show_movie(path_video: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            video_data = kna_reader.medium(path=path_video)
            return render_template("video.html", video=video_data)
        except Exception as e:
            logger.error(f"Video error: {e}")
            return _render_error("Video niet gevonden"), 404

    @app.route("/leden")
    @optional_login
    def view_leden():
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            leden = kna_reader.leden()
            return render_template("leden.html", leden=leden)
        except Exception as e:
            logger.error(f"Leden error: {e}")
            return _render_error("Fout bij laden ledenlijst"), 500

    @app.route("/voorstellingen")
    @optional_login
    def view_voorstellingen():
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            voorstellingen = kna_reader.voorstellingen()
            return render_template("voorstellingen.html", voorstellingen=voorstellingen)
        except Exception as e:
            logger.error(f"Voorstellingen error: {e}")
            return _render_error("Fout bij laden voorstellingen"), 500

    @app.route("/tijdslijn")
    @optional_login
    def view_tijdslijn():
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            tijdslijn = kna_reader.timeline()
            return render_template("tijdslijn.html", tijdslijn=tijdslijn)
        except Exception as e:
            logger.error(f"Tijdslijn error: {e}")
            return _render_error("Fout bij laden tijdslijn"), 500

    @app.route("/lid_media/<lid>")
    @optional_login
    def lid_media(lid: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            media = kna_reader.lid_media(id_lid=lid)
            lid_info = kna_reader.lid_info(id_lid=lid)
            return render_template("lid_media.html", lid=lid_info, media=media)
        except Exception as e:
            logger.error(f"Lid media error: {e}")
            return _render_error("Fout bij laden lid media"), 500

    @app.route("/voorstelling_media/<voorstelling>")
    @optional_login
    def voorstelling_media(voorstelling: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            info = kna_reader.voorstelling_info(voorstelling=voorstelling)
            media = kna_reader.voorstelling_media(voorstelling=voorstelling)
            return render_template("voorstelling_media.html", voorstelling=info, media=media)
        except Exception as e:
            logger.error(f"Voorstelling media error: {e}")
            return _render_error("Fout bij laden voorstelling media"), 500

    @app.route("/voorstelling_lid_media/<voorstelling>/<lid>")
    @optional_login
    def voorstelling_lid_media(voorstelling: str, lid: str):
        if not kna_reader:
            return _render_error("Database niet beschikbaar"), 503

        try:
            info = kna_reader.voorstelling_info(voorstelling=voorstelling)
            media = kna_reader.voorstelling_lid_media(voorstelling=voorstelling, lid=lid)
            return render_template("voorstelling_media.html", voorstelling=info, media=media)
        except Exception as e:
            logger.error(f"Voorstelling lid media error: {e}")
            return _render_error("Fout bij laden media"), 500


def _register_health_routes(app: Flask, kna_reader: KnaDataReader | None, config):
    """Register health check and monitoring routes"""

    @app.route("/health")
    def health():
        """Comprehensive health check"""
        status = {
            "status": "healthy",
            "users_db": DatabaseManager.check_users_db_health(),
        }

        if kna_reader:
            kna_engine = config.get_kna_engine()
            status["kna_db"] = DatabaseManager.check_kna_db_health(kna_engine)
        else:
            status["kna_db"] = {"status": "not_initialized"}

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
                    username="admin",
                    email="admin@kna-hillegom.local",
                    role="admin"
                )
                admin.set_password(admin_password)

                db.session.add(admin)
                db.session.commit()

                logger.info("Created default admin user")
                logger.warning(f"Default admin password is: {admin_password}")
            else:
                logger.info("Admin user already exists")
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")


def _render_error(message: str) -> str:
    """Render error template"""
    try:
        return render_template("error.html", message=message)
    except:
        # Fallback if template doesn't exist
        return f"<h1>Error</h1><p>{message}</p>"


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", False)
    )
