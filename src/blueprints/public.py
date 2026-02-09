"""
Public Routes Blueprint

Public-facing routes for the KNA History Archive:
- Home and about pages
- Media serving (CDN, images, videos, PDFs)
- Content browsing (members, performances, timeline)
- Health monitoring

All routes use dependency injection via helpers (DRY).
"""

import os

from flask import Blueprint, render_template, send_from_directory
from flask_login import login_required

from kna_data import DatabaseManager
from logging import logger

# Import shared helpers
from .helpers import get_kna_config, with_kna_reader

# Create blueprint
public_bp = Blueprint("public", __name__)


# ============================================================================
# Configuration: Optional Login
# ============================================================================


def _require_login() -> bool:
    """Check if login is required for all routes"""
    return os.getenv("REQUIRE_LOGIN", "false").lower() == "true"


def _optional_login(f):
    """Decorator that optionally requires login based on config"""
    return login_required(f) if _require_login() else f


# ============================================================================
# Static Pages
# ============================================================================


@public_bp.route("/")
@public_bp.route("/home")
def home():
    """Home page"""
    return render_template("home.html")


@public_bp.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="Over")


# ============================================================================
# Media Serving
# ============================================================================


@public_bp.route("/cdn/<path:filepath>")
@_optional_login
@with_kna_reader
def cdn(reader, filepath):
    """
    Serve media files via CDN endpoint.

    Args:
        reader: KnaDataReader (injected by decorator)
        filepath: Encoded file path
    """
    try:
        dir_path, filename = os.path.split(reader.decode(filepath))
        return send_from_directory(dir_path, filename, as_attachment=False)
    except Exception as e:
        logger.error(f"CDN error: {e}")
        return "File not found", 404


@public_bp.route("/image/<path_image>")
@_optional_login
@with_kna_reader
def show_image(reader, path_image: str):
    """
    Display image page.

    Args:
        reader: KnaDataReader (injected by decorator)
        path_image: Path to image
    """
    try:
        image_data = reader.medium(path=path_image)
        return render_template("image.html", image=image_data)
    except Exception as e:
        logger.error(f"Image error: {e}")
        return _render_error("Afbeelding niet gevonden"), 404


@public_bp.route("/pdf/<path_pdf>")
@_optional_login
def show_document(path_pdf: str):
    """
    Display PDF document.

    Args:
        path_pdf: Path to PDF
    """
    return render_template("pdf.html", file_pdf=path_pdf)


@public_bp.route("/video/<path_video>")
@_optional_login
@with_kna_reader
def show_movie(reader, path_video: str):
    """
    Display video page.

    Args:
        reader: KnaDataReader (injected by decorator)
        path_video: Path to video
    """
    try:
        video_data = reader.medium(path=path_video)
        return render_template("video.html", video=video_data)
    except Exception as e:
        logger.error(f"Video error: {e}")
        return _render_error("Video niet gevonden"), 404


# ============================================================================
# Content Browsing
# ============================================================================


@public_bp.route("/leden")
@_optional_login
@with_kna_reader
def view_leden(reader):
    """
    View members list.

    Args:
        reader: KnaDataReader (injected by decorator)
    """
    leden = reader.leden()
    return render_template("leden.html", leden=leden)


@public_bp.route("/voorstellingen")
@_optional_login
@with_kna_reader
def view_voorstellingen(reader):
    """
    View performances list.

    Args:
        reader: KnaDataReader (injected by decorator)
    """
    voorstellingen = reader.voorstellingen()
    return render_template("voorstellingen.html", voorstellingen=voorstellingen)


@public_bp.route("/tijdslijn")
@_optional_login
@with_kna_reader
def view_tijdslijn(reader):
    """
    View timeline.

    Args:
        reader: KnaDataReader (injected by decorator)
    """
    tijdslijn = reader.timeline()
    return render_template("tijdslijn.html", tijdslijn=tijdslijn)


# ============================================================================
# Media Galleries
# ============================================================================


@public_bp.route("/lid_media/<lid>")
@_optional_login
@with_kna_reader
def lid_media(reader, lid: str):
    """
    View member media gallery.

    Args:
        reader: KnaDataReader (injected by decorator)
        lid: Member ID
    """
    media = reader.lid_media(id_lid=lid)
    lid_info = reader.lid_info(id_lid=lid)
    return render_template("lid_media.html", lid=lid_info, media=media)


@public_bp.route("/voorstelling_media/<voorstelling>")
@_optional_login
@with_kna_reader
def voorstelling_media(reader, voorstelling: str):
    """
    View performance media gallery.

    Args:
        reader: KnaDataReader (injected by decorator)
        voorstelling: Performance reference
    """
    info = reader.voorstelling_info(voorstelling=voorstelling)
    media = reader.voorstelling_media(voorstelling=voorstelling)
    return render_template("voorstelling_media.html", voorstelling=info, media=media)


@public_bp.route("/voorstelling_lid_media/<voorstelling>/<lid>")
@_optional_login
@with_kna_reader
def voorstelling_lid_media(reader, voorstelling: str, lid: str):
    """
    View member media in specific performance.

    Args:
        reader: KnaDataReader (injected by decorator)
        voorstelling: Performance reference
        lid: Member ID
    """
    info = reader.voorstelling_info(voorstelling=voorstelling)
    media = reader.voorstelling_lid_media(voorstelling=voorstelling, lid=lid)
    return render_template("voorstelling_media.html", voorstelling=info, media=media)


# ============================================================================
# Monitoring & Health
# ============================================================================


@public_bp.route("/health")
def health():
    """
    Comprehensive health check endpoint.

    Checks:
    - Users database connection
    - KNA content database connection
    - Database table counts

    Returns:
        JSON response with health status and HTTP status code
    """
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

    # Determine overall status
    is_healthy = all(
        db_status.get("status") == "healthy"
        for db_status in [status["users_db"], status["kna_db"]]
    )
    status["status"] = "healthy" if is_healthy else "degraded"

    http_status = 200 if is_healthy else 503
    return status, http_status


# ============================================================================
# Error Handling
# ============================================================================


def _render_error(message: str) -> str:
    """
    Render error template with user-friendly message.

    Args:
        message: Error message to display

    Returns:
        Rendered HTML error page
    """
    try:
        return render_template("error.html", message=message)
    except Exception:
        # Fallback if template doesn't exist
        return f"<h1>Error</h1><p>{message}</p>"


@public_bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return _render_error("Pagina niet gevonden."), 404


@public_bp.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}", exc_info=True)
    return _render_error("Er is een interne fout opgetreden."), 500
