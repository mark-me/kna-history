"""
Admin Blueprint

Administrative functions for KNA History application.
Includes data upload, validation, and management features.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    session,
)
from werkzeug.utils import secure_filename

from kna_data import Config, KnaDataLoader
from logging_kna import logger

# Create blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Configuration
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = Path("/tmp/kna_uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(file):
    """Get file size in bytes"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


@admin_bp.route("/")
def index():
    """Admin dashboard"""
    return render_template("admin/dashboard.html")


@admin_bp.route("/upload")
def upload_page():
    """Excel upload page"""
    return render_template("admin/upload.html")


@admin_bp.route("/upload/validate", methods=["POST"])
def validate_upload():
    """
    Validate uploaded Excel file without loading.
    Returns validation results as JSON.
    """
    try:
        file, error_response = _get_uploaded_file()
        if error_response is not None:
            return error_response

        error_response = _validate_file_properties(file)
        if error_response is not None:
            return error_response

        temp_path, filename = _save_temp_file(file)

        # Validate Excel structure
        config = Config.for_production()
        loader = KnaDataLoader(config=config)

        validation = loader.validate_excel(str(temp_path))

        # Store temp path in session for later use
        if validation["valid"]:
            session["temp_file_path"] = str(temp_path)
            session["temp_file_name"] = filename
        else:
            # Clean up if invalid
            temp_path.unlink(missing_ok=True)

        return jsonify(validation)

    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return jsonify(
            {"valid": False, "errors": [f"Validation failed: {str(e)}"]}
        ), 500


def _get_uploaded_file():
    """Retrieve uploaded file from request, return (file, error_response_or_None)."""
    if "file" not in request.files:
        return None, (jsonify({"valid": False, "errors": ["No file provided"]}), 400)

    file = request.files["file"]

    if file.filename == "":
        return None, (jsonify({"valid": False, "errors": ["No file selected"]}), 400)

    return file, None


def _validate_file_properties(file):
    """Validate file type and size, return error_response_or_None."""
    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "valid": False,
                    "errors": [
                        f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                    ],
                }
            ),
            400,
        )

    file_size = get_file_size(file)
    if file_size > MAX_FILE_SIZE:
        return (
            jsonify(
                {
                    "valid": False,
                    "errors": [
                        f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
                    ],
                }
            ),
            400,
        )

    return None


def _save_temp_file(file):
    """Save uploaded file to a temporary path and return (temp_path, filename)."""
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"{timestamp}_{filename}"
    temp_path = UPLOAD_FOLDER / temp_filename
    file.save(temp_path)
    logger.info(f"File saved to {temp_path} for validation")
    return temp_path, filename


@admin_bp.route("/upload/load", methods=["POST"])
def load_data():
    """
    Load validated Excel file into database.
    File must have been validated first.
    """
    try:
        # Check if we have a validated file in session
        if "temp_file_path" not in session:
            return jsonify(
                {
                    "success": False,
                    "error": "No validated file found. Please validate first.",
                }
            ), 400

        temp_path = session.get("temp_file_path")
        filename = session.get("temp_file_name")

        if not os.path.exists(temp_path):
            return jsonify(
                {
                    "success": False,
                    "error": "Validated file no longer exists. Please re-upload.",
                }
            ), 400

        # Load data
        config = Config.for_production()
        loader = KnaDataLoader(config=config)

        logger.info(f"Loading data from {temp_path}")
        stats = loader.load_from_excel(temp_path)

        # Clean up temp file
        os.unlink(temp_path)
        session.pop("temp_file_path", None)
        session.pop("temp_file_name", None)

        logger.info(f"Data loaded successfully: {stats}")

        return jsonify(
            {
                "success": True,
                "message": f"Data loaded successfully from {filename}",
                "stats": stats,
            }
        )

    except Exception as e:
        logger.error(f"Load error: {e}", exc_info=True)

        # Clean up on error
        if "temp_file_path" in session:
            temp_path = session.get("temp_file_path")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            session.pop("temp_file_path", None)
            session.pop("temp_file_name", None)

        return jsonify({"success": False, "error": f"Load failed: {str(e)}"}), 500


@admin_bp.route("/upload/cancel", methods=["POST"])
def cancel_upload():
    """Cancel upload and clean up temporary file"""
    try:
        if "temp_file_path" in session:
            temp_path = session.get("temp_file_path")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cancelled upload, deleted {temp_path}")

            session.pop("temp_file_path", None)
            session.pop("temp_file_name", None)

        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Cancel error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/data/stats")
def data_stats():
    """Get current database statistics"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        # Query counts from database
        import pandas as pd

        stats = {}

        # Members count
        df = pd.read_sql("SELECT COUNT(*) as count FROM lid", con=reader.engine)
        stats["members"] = int(df.iloc[0]["count"])

        # Performances count
        df = pd.read_sql(
            "SELECT COUNT(*) as count FROM uitvoering WHERE type='Uitvoering'",
            con=reader.engine,
        )
        stats["performances"] = int(df.iloc[0]["count"])

        # Roles count
        df = pd.read_sql("SELECT COUNT(*) as count FROM rol", con=reader.engine)
        stats["roles"] = int(df.iloc[0]["count"])

        # Files count
        df = pd.read_sql("SELECT COUNT(*) as count FROM file", con=reader.engine)
        stats["files"] = int(df.iloc[0]["count"])

        # Media types count
        df = pd.read_sql(
            "SELECT type_media, COUNT(*) as count FROM file GROUP BY type_media",
            con=reader.engine,
        )
        stats["media_by_type"] = df.to_dict("records")

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/thumbnails/regenerate", methods=["POST"])
def regenerate_thumbnails():
    """Regenerate all thumbnails"""
    try:
        config = Config.for_production()
        loader = KnaDataLoader(config=config)

        count = loader._generate_thumbnails()

        return jsonify(
            {
                "success": True,
                "message": f"Generated {count} thumbnails",
                "count": count,
            }
        )

    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# Error handlers for blueprint
@admin_bp.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify(
        {
            "valid": False,
            "errors": [
                f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            ],
        }
    ), 413
