"""
Blueprint Helpers

Shared utilities for all blueprints.
Eliminates code duplication and provides consistent patterns.
"""

from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user

from logging import logger


# ============================================================================
# Service Access (DRY - get from app context)
# ============================================================================


def get_kna_config():
    """
    Get KNA configuration from app context.

    Returns:
        BaseConfig: Configuration object

    Raises:
        RuntimeError: If config not initialized
    """
    if config := current_app.config.get("KNA_CONFIG"):
        return config
    else:
        raise RuntimeError("KNA_CONFIG not initialized in app context")


def get_kna_reader():
    """
    Get KNA data reader from app context.

    Returns:
        KnaDataReader: Reader instance

    Raises:
        RuntimeError: If reader not initialized
    """
    if reader := current_app.config.get("KNA_READER"):
        return reader
    else:
        raise RuntimeError("KNA_READER not initialized in app context")


def get_kna_loader():
    """
    Get KNA data loader from app context.

    Returns:
        KnaDataLoader: Loader instance

    Raises:
        RuntimeError: If loader not initialized
    """
    if loader := current_app.config.get("KNA_LOADER"):
        return loader
    else:
        raise RuntimeError("KNA_LOADER not initialized in app context")


# ============================================================================
# Authentication Decorators (DRY - no duplication)
# ============================================================================


def admin_required(f):
    """
    Decorator to require admin access.

    Usage:
        @app.route('/admin/dashboard')
        @login_required
        @admin_required
        def dashboard():
            ...
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Log in om deze pagina te bekijken.", "warning")
            return redirect(url_for("auth.login"))

        if not current_user.is_admin:
            flash("Alleen administrators hebben toegang tot dit gedeelte.", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return decorated


# ============================================================================
# File Validation (DRY - no duplication)
# ============================================================================


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    """
    Check if file extension is allowed.

    Args:
        filename: Filename to check
        allowed_extensions: Set of allowed extensions (without dots)

    Returns:
        bool: True if allowed, False otherwise

    Example:
        >>> allowed_file('photo.jpg', {'jpg', 'png'})
        True
        >>> allowed_file('document.pdf', {'jpg', 'png'})
        False
    """
    if not filename or "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


# ============================================================================
# Error Handling Decorators
# ============================================================================


def with_kna_reader(f):
    """
    Decorator that provides KNA reader with error handling.

    Injects reader as first argument to the decorated function.
    Handles errors gracefully with user-friendly messages.

    Usage:
        @app.route('/leden')
        @with_kna_reader
        def view_leden(reader):
            leden = reader.leden()
            return render_template('leden.html', leden=leden)
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            reader = get_kna_reader()
            return f(reader, *args, **kwargs)
        except RuntimeError as e:
            logger.error(f"Reader not available: {e}")
            flash(
                "Database niet beschikbaar. Neem contact op met de beheerder.", "danger"
            )
            return redirect(url_for("home"))
        except Exception as e:
            logger.error(f"Reader error in {f.__name__}: {e}", exc_info=True)
            flash("Er is een fout opgetreden bij het laden van gegevens.", "danger")
            return redirect(url_for("home"))

    return decorated


def with_kna_loader(f):
    """
    Decorator that provides KNA loader with error handling.

    Injects loader as first argument to the decorated function.

    Usage:
        @app.route('/admin/load')
        @with_kna_loader
        def load_data(loader):
            stats = loader.load_from_excel(path)
            return jsonify(stats)
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            loader = get_kna_loader()
            return f(loader, *args, **kwargs)
        except RuntimeError as e:
            logger.error(f"Loader not available: {e}")
            flash("Data loader niet beschikbaar.", "danger")
            return redirect(url_for("admin.index"))
        except Exception as e:
            logger.error(f"Loader error in {f.__name__}: {e}", exc_info=True)
            flash("Er is een fout opgetreden.", "danger")
            return redirect(url_for("admin.index"))

    return decorated


# ============================================================================
# Dutch Name Utilities (DRY - shared logic)
# ============================================================================


def calculate_sort_name(achternaam: str) -> str:
    """
    Calculate sortable last name handling Dutch prefixes.

    Dutch names like "van der Berg" should sort under "Berg, van der"

    Args:
        achternaam: Last name (may include prefix)

    Returns:
        str: Sortable version of the name

    Examples:
        >>> calculate_sort_name("van der Berg")
        'Berg, van der'
        >>> calculate_sort_name("de Vries")
        'Vries, de'
        >>> calculate_sort_name("Jansen")
        'Jansen'
    """
    if not achternaam:
        return "zzzzzzzz"  # Sort empty names last

    prefixes = ["van der", "van den", "van de", "van", "de", "v.d."]
    achternaam_lower = achternaam.lower()

    for prefix in prefixes:
        if achternaam_lower.startswith(f"{prefix} "):
            rest = achternaam[len(prefix) + 1 :]
            return f"{rest}, {prefix}"

    return achternaam


# ============================================================================
# File Size Utilities
# ============================================================================


def get_file_size(file) -> int:
    """
    Get uploaded file size in bytes.

    Args:
        file: FileStorage object from Flask request.files

    Returns:
        int: File size in bytes
    """
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Seek back to start
    return size


def format_file_size(bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"
