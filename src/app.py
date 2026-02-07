"""
KNA History Web Application

Flask web application for browsing the KNA theatre group history archive.
"""

import os

from flask import (
    Flask,
    render_template,
    send_from_directory,
)
from flask_login import LoginManager, login_required

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.data_entry import data_entry_bp  # NEW
from kna_data import KnaDataReader, User, db
from kna_data.config import get_config
from logging_kna import logger

# Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration environment ('development', 'production', 'testing')
                    If None, reads from FLASK_ENV or KNA_ENV environment variable

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    logger.info(f"Starting app with {config_obj.__class__.__name__}")
    logger.info(f"Database: {config_obj.SQLITE_PATH}")
    logger.info(f"Resources dir: {config_obj.DIR_RESOURCES}")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(data_entry_bp, url_prefix="/data-entry")

    # Initialize database reader - with error handling
    try:
        db_reader = KnaDataReader(config=config_obj)
        logger.info("Database reader initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database reader: {e}")
        db_reader = None

    # Determine if routes should require login
    # Set REQUIRE_LOGIN=true in environment to protect all routes
    require_login = os.getenv("REQUIRE_LOGIN", "false").lower() == "true"
    logger.info(f"Route protection: {'enabled' if require_login else 'disabled'}")

    # Decorator to optionally require login
    def optional_login(f):
        return login_required(f) if require_login else f

    # Public routes (home, about, viewer content)
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
        """Serve media files via CDN endpoint"""
        if db_reader is None:
            return "Database not available", 503

        dir, filename = os.path.split(db_reader.decode(filepath))
        logger.info(f"Serve media CDN - Directory: {dir} - File: {filename}")
        return send_from_directory(dir, filename, as_attachment=False)

    @app.route("/image/<path_image>")
    @optional_login
    def show_image(path_image: str):
        """Display image page"""
        if db_reader is None:
            return "Database not available", 503

        logger.info(f"Show image - filepath: {path_image}")
        dict_image = db_reader.medium(path=path_image)
        return render_template("image.html", image=dict_image)

    @app.route("/pdf/<path_pdf>")
    @optional_login
    def show_document(path_pdf: str):
        """Display PDF document"""
        if db_reader is None:
            return "Database not available", 503

        logger.info(f"Show PDF - {path_pdf}")
        return render_template("pdf.html", file_pdf=path_pdf)

    @app.route("/video/<path_video>")
    @optional_login
    def show_movie(path_video: str):
        """Display video page"""
        if db_reader is None:
            return "Database not available", 503

        logger.info(f"Show video - {path_video}")
        dict_video = db_reader.medium(path=path_video)
        return render_template("video.html", video=dict_video)

    @app.route("/leden")
    @optional_login
    def view_leden():
        """Page for viewing members"""
        if db_reader is None:
            return render_template("error.html",
                                 message="Database is niet beschikbaar. Neem contact op met de beheerder."), 503

        try:
            lst_leden = db_reader.leden()
            return render_template("leden.html", leden=lst_leden)
        except Exception as e:
            logger.error(f"Error loading members: {e}")
            return render_template("error.html",
                                 message="Er is een fout opgetreden bij het laden van de ledenlijst."), 500

    @app.route("/voorstellingen")
    @optional_login
    def view_voorstellingen():
        """Page for viewing performances"""
        if db_reader is None:
            return render_template("error.html",
                                 message="Database is niet beschikbaar. Neem contact op met de beheerder."), 503

        try:
            lst_voorstelling = db_reader.voorstellingen()
            return render_template("voorstellingen.html", voorstellingen=lst_voorstelling)
        except Exception as e:
            logger.error(f"Error loading performances: {e}")
            return render_template("error.html",
                                 message="Er is een fout opgetreden bij het laden van de voorstellingen."), 500

    @app.route("/tijdslijn")
    @optional_login
    def view_tijdslijn():
        """Page for viewing timeline"""
        if db_reader is None:
            return render_template("error.html",
                                 message="Database is niet beschikbaar. Neem contact op met de beheerder."), 503

        try:
            lst_timeline = db_reader.timeline()
            return render_template("tijdslijn.html", tijdslijn=lst_timeline)
        except Exception as e:
            logger.error(f"Error loading timeline: {e}")
            return render_template("error.html",
                                 message="Er is een fout opgetreden bij het laden van de tijdslijn."), 500

    @app.route("/lid_media/<lid>")
    @optional_login
    def lid_media(lid: str):
        """Page for member media"""
        if db_reader is None:
            return "Database not available", 503

        logger.info(f"Leden media voor {lid}")
        lst_media = db_reader.lid_media(id_lid=lid)
        dict_lid = db_reader.lid_info(id_lid=lid)
        return render_template("lid_media.html", lid=dict_lid, media=lst_media)

    @app.route("/voorstelling_media/<voorstelling>")
    @optional_login
    def voorstelling_media(voorstelling: str):
        """Page for performance media"""
        if db_reader is None:
            return "Database not available", 503

        dict_voorstelling = db_reader.voorstelling_info(voorstelling=voorstelling)
        lst_media = db_reader.voorstelling_media(voorstelling=voorstelling)
        logger.info(f"Get media voor voorstelling {voorstelling}")
        return render_template(
            "voorstelling_media.html", voorstelling=dict_voorstelling, media=lst_media
        )

    @app.route("/voorstelling_lid_media/<voorstelling>/<lid>")
    @optional_login
    def voorstelling_lid_media(voorstelling: str, lid: str):
        """Page for member media in a specific performance"""
        if db_reader is None:
            return "Database not available", 503

        dict_voorstelling = db_reader.voorstelling_info(voorstelling=voorstelling)
        lst_media = db_reader.voorstelling_lid_media(voorstelling=voorstelling, lid=lid)
        logger.info(f"Get media voor voorstelling {voorstelling} van {lid}")
        return render_template(
            "voorstelling_media.html", voorstelling=dict_voorstelling, media=lst_media
        )

    @app.route("/health")
    def health():
        """Health check endpoint"""
        health_status = {
            "status": "healthy",
            "database_reader": "connected" if db_reader is not None else "not initialized"
        }

        try:
            if db_reader is not None:
                with db_reader.engine.connect() as conn:
                    conn.execute("SELECT 1")
                health_status["database_connection"] = "connected"
            else:
                health_status["database_connection"] = "not available"
                health_status["status"] = "degraded"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status, 503

        status_code = 200 if health_status["status"] == "healthy" else 503
        return health_status, status_code

    # Initialize database tables and create default admin user
    with app.app_context():
        db.create_all()

        # Create default admin user if none exists
        if not User.query.filter_by(role="admin").first():
            from werkzeug.security import generate_password_hash

            admin_password = os.getenv("ADMIN_PASSWORD", "admin2026!")
            admin = User(
                username="admin",
                email="admin@kna-hillegom.local",
                role="admin"
            )
            admin.password_hash = generate_password_hash(admin_password)
            db.session.add(admin)
            db.session.commit()
            logger.info("Created default admin user")

    return app


if __name__ == "__main__":
    # For local development
    app = create_app("development")
    app.run(debug=True, host="0.0.0.0", port=5000)
