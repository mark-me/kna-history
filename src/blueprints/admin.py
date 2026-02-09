"""
Admin Blueprint

Administrative functions for KNA History application.
Includes data upload, validation, and management features.
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from kna_data import User, db
from logging import logger

from .helpers import (
    allowed_file,
    get_file_size,
    with_kna_loader,
    with_kna_reader,
)

# Create blueprint
admin_bp = Blueprint("admin", __name__)

# Configuration
ALLOWED_EXTENSIONS = {"xlsx", "xls"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = Path("/tmp/kna_uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@admin_bp.before_request
@login_required
def require_login_for_admin():
    """Require login for all admin routes"""
    if not current_user.is_admin:
        flash("Alleen beheerders hebben toegang tot dit gedeelte.", "danger")
        return redirect(url_for("auth.login"))


# ============================================================================
# Admin Dashboard
# ============================================================================


@admin_bp.route("/")
def index():
    """Admin dashboard"""
    return render_template("admin/dashboard.html")


# ============================================================================
# Excel Upload (Uses helpers - DRY!)
# ============================================================================


@admin_bp.route("/upload")
def upload_page():
    """Excel upload page"""
    return render_template("admin/upload.html")


@admin_bp.route("/upload/validate", methods=["POST"])
@with_kna_loader  # Loader injected automatically!
def validate_upload(loader):
    """Validate uploaded Excel file (loader injected by decorator)"""
    try:
        # Get file
        if "file" not in request.files:
            return jsonify({"valid": False, "errors": ["No file provided"]}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"valid": False, "errors": ["No file selected"]}), 400

        # Validate file type using helper (DRY!)
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify(
                {
                    "valid": False,
                    "errors": [
                        f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                    ],
                }
            ), 400

        # Validate file size using helper (DRY!)
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify(
                {
                    "valid": False,
                    "errors": [f"File too large. Max: {MAX_FILE_SIZE / 1024 / 1024}MB"],
                }
            ), 400

        # Save temporary file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = UPLOAD_FOLDER / temp_filename
        file.save(temp_path)
        logger.info(f"File saved: {temp_path}")

        # Validate Excel structure (loader already injected!)
        validation = loader.validate_excel(str(temp_path))

        # Store for later use
        if validation["valid"]:
            session["temp_file_path"] = str(temp_path)
            session["temp_file_name"] = filename
        else:
            temp_path.unlink(missing_ok=True)

        return jsonify(validation)

    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return jsonify(
            {"valid": False, "errors": [f"Validation failed: {str(e)}"]}
        ), 500


@admin_bp.route("/upload/load", methods=["POST"])
@with_kna_loader  # Loader injected automatically!
def load_data(loader):
    """Load validated Excel file (loader injected by decorator)"""
    try:
        # Check session
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

        # Load data (loader already injected!)
        logger.info(f"Loading data from {temp_path}")
        stats = loader.load_from_excel(temp_path)

        # Cleanup
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

        # Cleanup on error
        if "temp_file_path" in session:
            temp_path = session.get("temp_file_path")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            session.pop("temp_file_path", None)
            session.pop("temp_file_name", None)

        return jsonify({"success": False, "error": f"Load failed: {str(e)}"}), 500


@admin_bp.route("/upload/cancel", methods=["POST"])
def cancel_upload():
    """Cancel upload and clean up"""
    try:
        if "temp_file_path" in session:
            temp_path = session.get("temp_file_path")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cancelled upload: {temp_path}")

            session.pop("temp_file_path", None)
            session.pop("temp_file_name", None)

        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Cancel error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Database Statistics (Uses helpers - DRY!)
# ============================================================================


@admin_bp.route("/data/stats")
@with_kna_reader  # Reader injected automatically!
def data_stats(reader):
    """Get database statistics (reader injected by decorator)"""
    try:
        # All queries use the same reader instance (efficient!)
        df = pd.read_sql("SELECT COUNT(*) as count FROM lid", con=reader.engine)
        stats = {"members": int(df.iloc[0]["count"])}
        df = pd.read_sql(
            "SELECT COUNT(*) as count FROM uitvoering WHERE type='Uitvoering'",
            con=reader.engine,
        )
        stats["performances"] = int(df.iloc[0]["count"])

        df = pd.read_sql("SELECT COUNT(*) as count FROM rol", con=reader.engine)
        stats["roles"] = int(df.iloc[0]["count"])

        df = pd.read_sql("SELECT COUNT(*) as count FROM file", con=reader.engine)
        stats["files"] = int(df.iloc[0]["count"])

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
@with_kna_loader  # Loader injected automatically!
def regenerate_thumbnails(loader):
    """Regenerate thumbnails (loader injected by decorator)"""
    try:
        count = loader._generate_thumbnails()

        return jsonify(
            {
                "success": True,
                "message": f"Generated {count} thumbnails",
                "count": count,
            }
        )

    except Exception as e:
        logger.error(f"Thumbnail error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# User Management
# ============================================================================


@admin_bp.route("/users")
def list_users():
    """List all users"""
    users = User.query.order_by(User.username).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    """Create new user"""
    if request.method != "POST":
        return render_template(
            "admin/user_form.html", user=None, form_action=url_for("admin.create_user")
        )
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role", "viewer")

    if User.query.filter_by(username=username).first():
        flash("Deze gebruikersnaam is al in gebruik.", "danger")
        return redirect(url_for("admin.create_user"))

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f"Gebruiker {username} succesvol aangemaakt.", "success")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    """Edit existing user"""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.role = request.form.get("role", user.role)

        if password := request.form.get("password"):
            user.set_password(password)

        db.session.commit()
        flash("Gebruiker bijgewerkt.", "success")
        return redirect(url_for("admin.list_users"))

    return render_template(
        "admin/user_form.html",
        user=user,
        form_action=url_for("admin.edit_user", user_id=user_id),
    )


@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Delete user"""
    if current_user.id == user_id:
        flash("Je kunt jezelf niet verwijderen.", "danger")
    else:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("Gebruiker verwijderd.", "success")

    return redirect(url_for("admin.list_users"))


# ============================================================================
# Error Handlers
# ============================================================================


@admin_bp.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify(
        {
            "valid": False,
            "errors": [f"File too large. Maximum: {MAX_FILE_SIZE / 1024 / 1024}MB"],
        }
    ), 413
