"""
Data Entry Blueprint

Interactive data entry for KNA History application.
Allows adding/editing members, performances, roles, and media files.
"""

from pathlib import Path

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import text

from kna_data import Config, KnaDataReader
from logging_kna import logger

# Create blueprint
data_entry_bp = Blueprint("data_entry", __name__)

# Configuration
ALLOWED_MEDIA_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "mp4"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for media files


def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Alleen administrators hebben toegang tot dit gedeelte.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename: str):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_MEDIA_EXTENSIONS


def calculate_sort_name(achternaam):
    """Calculate sortable last name handling Dutch prefixes"""
    if not achternaam:
        return "zzzzzzzz"

    tussenvoegsels = ["van der", "van den", "van de", "van", "de", "v.d."]
    achternaam_lower = achternaam.lower()

    for tussenvoegsel in tussenvoegsels:
        if achternaam_lower.startswith(f"{tussenvoegsel} "):
            rest = achternaam[len(tussenvoegsel)+1:]
            return f"{rest}, {tussenvoegsel}"

    return achternaam


# ============================================================================
# Dashboard
# ============================================================================

@data_entry_bp.route("/")
@login_required
@admin_required
def index():
    """Data entry dashboard with statistics"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        # Get statistics
        with reader.engine.connect() as conn:
            stats = {
                'members': conn.execute(text("SELECT COUNT(*) as count FROM lid")).fetchone()[0],
                'performances': conn.execute(text("SELECT COUNT(*) as count FROM uitvoering WHERE type='Uitvoering'")).fetchone()[0],
                'roles': conn.execute(text("SELECT COUNT(*) as count FROM rol")).fetchone()[0],
                'files': conn.execute(text("SELECT COUNT(*) as count FROM file")).fetchone()[0],
            }

        return render_template("data_entry/dashboard.html", stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash("Kan statistieken niet laden.", "warning")
        return render_template("data_entry/dashboard.html", stats=None)


# ============================================================================
# Members (Leden) Management
# ============================================================================

@data_entry_bp.route("/members")
@login_required
@admin_required
def list_members():
    """List all members"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id_lid, Voornaam, Achternaam, Geboortedatum, Startjaar, gdpr_permission
                FROM lid
                ORDER BY achternaam_sort
            """))
            members = [dict(row._mapping) for row in result]

        return render_template("data_entry/members_list.html", members=members)
    except Exception as e:
        logger.error(f"List members error: {e}")
        flash("Kan ledenlijst niet laden.", "danger")
        return redirect(url_for("data_entry.index"))


@data_entry_bp.route("/members/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_member():
    """Add new member"""
    if request.method == "POST":
        try:
            id_lid = request.form.get('id_lid')
            voornaam = request.form.get('voornaam')
            achternaam = request.form.get('achternaam')
            geboortedatum = request.form.get('geboortedatum') or None
            startjaar = request.form.get('startjaar', type=int) or None
            gdpr_permission = 1 if request.form.get('gdpr_permission') else 0

            # Calculate sort name
            achternaam_sort = calculate_sort_name(achternaam)

            config = Config.for_production()
            reader = KnaDataReader(config=config)

            with reader.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO lid (id_lid, Voornaam, Achternaam, achternaam_sort, Geboortedatum, Startjaar, gdpr_permission)
                    VALUES (:id_lid, :voornaam, :achternaam, :achternaam_sort, :geboortedatum, :startjaar, :gdpr_permission)
                """), {
                    'id_lid': id_lid,
                    'voornaam': voornaam,
                    'achternaam': achternaam,
                    'achternaam_sort': achternaam_sort,
                    'geboortedatum': geboortedatum,
                    'startjaar': startjaar,
                    'gdpr_permission': gdpr_permission
                })
                conn.commit()

            flash(f'Lid {voornaam} {achternaam} succesvol toegevoegd!', 'success')
            return redirect(url_for('data_entry.list_members'))

        except Exception as e:
            logger.error(f"Add member error: {e}")
            flash(f'Fout bij toevoegen lid: {str(e)}', 'danger')

    return render_template("data_entry/member_form.html", member=None)


@data_entry_bp.route("/members/edit/<id_lid>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_member(id_lid):
    """Edit existing member"""
    config = Config.for_production()
    reader = KnaDataReader(config=config)

    try:
        # Get member data
        with reader.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id_lid, Voornaam, Achternaam, Geboortedatum, Startjaar, gdpr_permission
                FROM lid WHERE id_lid = :id_lid
            """), {'id_lid': id_lid})
            member = result.fetchone()

            if not member:
                flash("Lid niet gevonden.", "danger")
                return redirect(url_for('data_entry.list_members'))

            member = dict(member._mapping)

        if request.method == "POST":
            try:
                voornaam = request.form.get('voornaam')
                achternaam = request.form.get('achternaam')
                geboortedatum = request.form.get('geboortedatum') or None
                startjaar = request.form.get('startjaar', type=int) or None
                gdpr_permission = 1 if request.form.get('gdpr_permission') else 0

                # Calculate sort name
                achternaam_sort = calculate_sort_name(achternaam)

                with reader.engine.connect() as conn:
                    conn.execute(text("""
                        UPDATE lid
                        SET Voornaam = :voornaam,
                            Achternaam = :achternaam,
                            achternaam_sort = :achternaam_sort,
                            Geboortedatum = :geboortedatum,
                            Startjaar = :startjaar,
                            gdpr_permission = :gdpr_permission
                        WHERE id_lid = :id_lid
                    """), {
                        'voornaam': voornaam,
                        'achternaam': achternaam,
                        'achternaam_sort': achternaam_sort,
                        'geboortedatum': geboortedatum,
                        'startjaar': startjaar,
                        'gdpr_permission': gdpr_permission,
                        'id_lid': id_lid
                    })
                    conn.commit()

                flash('Lid bijgewerkt!', 'success')
                return redirect(url_for('data_entry.list_members'))

            except Exception as e:
                logger.error(f"Edit member error: {e}")
                flash(f'Fout bij bijwerken lid: {str(e)}', 'danger')

        return render_template("data_entry/member_form.html", member=member)

    except Exception as e:
        logger.error(f"Load member error: {e}")
        flash("Kan lid niet laden.", "danger")
        return redirect(url_for('data_entry.list_members'))


@data_entry_bp.route("/members/delete/<id_lid>", methods=["POST"])
@login_required
@admin_required
def delete_member(id_lid):
    """Delete member"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            conn.execute(text("DELETE FROM lid WHERE id_lid = :id_lid"), {'id_lid': id_lid})
            conn.commit()

        flash('Lid verwijderd.', 'success')
    except Exception as e:
        logger.error(f"Delete member error: {e}")
        flash(f'Fout bij verwijderen lid: {str(e)}', 'danger')

    return redirect(url_for('data_entry.list_members'))


# ============================================================================
# Performances (Voorstellingen) Management
# ============================================================================

@data_entry_bp.route("/performances")
@login_required
@admin_required
def list_performances():
    """List all performances"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT ref_uitvoering, titel, auteur, jaar, type, datum_van, datum_tot, regie, qty_media
                FROM uitvoering
                ORDER BY jaar DESC
            """))
            performances = [dict(row._mapping) for row in result]

        return render_template("data_entry/performances_list.html", performances=performances)
    except Exception as e:
        logger.error(f"List performances error: {e}")
        flash("Kan voorstellingenlijst niet laden.", "danger")
        return redirect(url_for("data_entry.index"))


@data_entry_bp.route("/performances/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_performance():
    """Add new performance"""
    if request.method == "POST":
        try:
            ref_uitvoering = request.form.get('ref_uitvoering')
            titel = request.form.get('titel')
            auteur = request.form.get('auteur')
            jaar = request.form.get('jaar', type=int)
            type_uitvoering = request.form.get('type', 'Uitvoering')
            datum_van = request.form.get('datum_van') or None
            datum_tot = request.form.get('datum_tot') or None
            folder = request.form.get('folder')
            regie = request.form.get('regie')

            config = Config.for_production()
            reader = KnaDataReader(config=config)

            with reader.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO uitvoering
                    (ref_uitvoering, titel, auteur, jaar, type, datum_van, datum_tot, folder, regie, qty_media)
                    VALUES (:ref_uitvoering, :titel, :auteur, :jaar, :type, :datum_van, :datum_tot, :folder, :regie, 0)
                """), {
                    'ref_uitvoering': ref_uitvoering,
                    'titel': titel,
                    'auteur': auteur,
                    'jaar': jaar,
                    'type': type_uitvoering,
                    'datum_van': datum_van,
                    'datum_tot': datum_tot,
                    'folder': folder,
                    'regie': regie
                })
                conn.commit()

            flash(f'Voorstelling "{titel}" succesvol toegevoegd!', 'success')
            return redirect(url_for('data_entry.list_performances'))

        except Exception as e:
            logger.error(f"Add performance error: {e}")
            flash(f'Fout bij toevoegen voorstelling: {str(e)}', 'danger')

    return render_template("data_entry/performance_form.html", performance=None)


@data_entry_bp.route("/performances/edit/<ref_uitvoering>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_performance(ref_uitvoering):
    """Edit existing performance"""
    config = Config.for_production()
    reader = KnaDataReader(config=config)

    try:
        # Get performance data
        with reader.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT ref_uitvoering, titel, auteur, jaar, type, datum_van, datum_tot, folder, regie
                FROM uitvoering WHERE ref_uitvoering = :ref_uitvoering
            """), {'ref_uitvoering': ref_uitvoering})
            performance = result.fetchone()

            if not performance:
                flash("Voorstelling niet gevonden.", "danger")
                return redirect(url_for('data_entry.list_performances'))

            performance = dict(performance._mapping)

        if request.method == "POST":
            try:
                titel = request.form.get('titel')
                auteur = request.form.get('auteur')
                jaar = request.form.get('jaar', type=int)
                type_uitvoering = request.form.get('type')
                datum_van = request.form.get('datum_van') or None
                datum_tot = request.form.get('datum_tot') or None
                folder = request.form.get('folder')
                regie = request.form.get('regie')

                with reader.engine.connect() as conn:
                    conn.execute(text("""
                        UPDATE uitvoering
                        SET titel = :titel,
                            auteur = :auteur,
                            jaar = :jaar,
                            type = :type,
                            datum_van = :datum_van,
                            datum_tot = :datum_tot,
                            folder = :folder,
                            regie = :regie
                        WHERE ref_uitvoering = :ref_uitvoering
                    """), {
                        'titel': titel,
                        'auteur': auteur,
                        'jaar': jaar,
                        'type': type_uitvoering,
                        'datum_van': datum_van,
                        'datum_tot': datum_tot,
                        'folder': folder,
                        'regie': regie,
                        'ref_uitvoering': ref_uitvoering
                    })
                    conn.commit()

                flash('Voorstelling bijgewerkt!', 'success')
                return redirect(url_for('data_entry.list_performances'))

            except Exception as e:
                logger.error(f"Edit performance error: {e}")
                flash(f'Fout bij bijwerken voorstelling: {str(e)}', 'danger')

        return render_template("data_entry/performance_form.html", performance=performance)

    except Exception as e:
        logger.error(f"Load performance error: {e}")
        flash("Kan voorstelling niet laden.", "danger")
        return redirect(url_for('data_entry.list_performances'))


@data_entry_bp.route("/performances/delete/<ref_uitvoering>", methods=["POST"])
@login_required
@admin_required
def delete_performance(ref_uitvoering):
    """Delete performance"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            conn.execute(text("DELETE FROM uitvoering WHERE ref_uitvoering = :ref_uitvoering"),
                        {'ref_uitvoering': ref_uitvoering})
            conn.commit()

        flash('Voorstelling verwijderd.', 'success')
    except Exception as e:
        logger.error(f"Delete performance error: {e}")
        flash(f'Fout bij verwijderen voorstelling: {str(e)}', 'danger')

    return redirect(url_for('data_entry.list_performances'))


# ============================================================================
# Roles (Rollen) Management
# ============================================================================

@data_entry_bp.route("/performances/<ref_uitvoering>/roles")
@login_required
@admin_required
def manage_roles(ref_uitvoering):
    """Manage roles for a performance"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            # Get performance info
            result = conn.execute(text("""
                SELECT ref_uitvoering, titel, jaar
                FROM uitvoering WHERE ref_uitvoering = :ref_uitvoering
            """), {'ref_uitvoering': ref_uitvoering})
            performance = dict(result.fetchone()._mapping)

            # Get roles for this performance
            result = conn.execute(text("""
                SELECT r.id_lid, r.rol, r.rol_bijnaam, l.Voornaam, l.Achternaam
                FROM rol r
                LEFT JOIN lid l ON l.id_lid = r.id_lid
                WHERE r.ref_uitvoering = :ref_uitvoering
                ORDER BY r.rol, l.achternaam_sort
            """), {'ref_uitvoering': ref_uitvoering})
            roles = [dict(row._mapping) for row in result]

            # Get all members for dropdown
            result = conn.execute(text("""
                SELECT id_lid, Voornaam, Achternaam
                FROM lid
                WHERE gdpr_permission = 1
                ORDER BY achternaam_sort
            """))
            members = [dict(row._mapping) for row in result]

        return render_template("data_entry/roles_manage.html",
                             performance=performance,
                             roles=roles,
                             members=members)
    except Exception as e:
        logger.error(f"Manage roles error: {e}")
        flash("Kan rollen niet laden.", "danger")
        return redirect(url_for('data_entry.list_performances'))


@data_entry_bp.route("/performances/<ref_uitvoering>/roles/add", methods=["POST"])
@login_required
@admin_required
def add_role(ref_uitvoering):
    """Add role to performance"""
    try:
        id_lid = request.form.get('id_lid')
        rol = request.form.get('rol')
        rol_bijnaam = request.form.get('rol_bijnaam')

        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO rol (ref_uitvoering, id_lid, rol, rol_bijnaam, qty_media)
                VALUES (:ref_uitvoering, :id_lid, :rol, :rol_bijnaam, 0)
            """), {
                'ref_uitvoering': ref_uitvoering,
                'id_lid': id_lid,
                'rol': rol,
                'rol_bijnaam': rol_bijnaam
            })
            conn.commit()

        flash('Rol toegevoegd!', 'success')
    except Exception as e:
        logger.error(f"Add role error: {e}")
        flash(f'Fout bij toevoegen rol: {str(e)}', 'danger')

    return redirect(url_for('data_entry.manage_roles', ref_uitvoering=ref_uitvoering))


@data_entry_bp.route("/performances/<ref_uitvoering>/roles/<id_lid>/delete", methods=["POST"])
@login_required
@admin_required
def delete_role(ref_uitvoering, id_lid):
    """Delete role from performance"""
    try:
        rol = request.form.get('rol')

        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            conn.execute(text("""
                DELETE FROM rol
                WHERE ref_uitvoering = :ref_uitvoering
                AND id_lid = :id_lid
                AND rol = :rol
            """), {
                'ref_uitvoering': ref_uitvoering,
                'id_lid': id_lid,
                'rol': rol
            })
            conn.commit()

        flash('Rol verwijderd.', 'success')
    except Exception as e:
        logger.error(f"Delete role error: {e}")
        flash(f'Fout bij verwijderen rol: {str(e)}', 'danger')

    return redirect(url_for('data_entry.manage_roles', ref_uitvoering=ref_uitvoering))


# ============================================================================
# Media Upload
# ============================================================================

@data_entry_bp.route("/performances/<ref_uitvoering>/media")
@login_required
@admin_required
def manage_media(ref_uitvoering):
    """Manage media for a performance"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        with reader.engine.connect() as conn:
            # Get performance info
            result = conn.execute(text("""
                SELECT ref_uitvoering, titel, jaar, folder
                FROM uitvoering WHERE ref_uitvoering = :ref_uitvoering
            """), {'ref_uitvoering': ref_uitvoering})
            performance = dict(result.fetchone()._mapping)

            # Get media for this performance
            result = conn.execute(text("""
                SELECT bestand, type_media, file_ext
                FROM file
                WHERE ref_uitvoering = :ref_uitvoering
                ORDER BY type_media, bestand
            """), {'ref_uitvoering': ref_uitvoering})
            media_files = [dict(row._mapping) for row in result]

            # Get all members for tagging
            result = conn.execute(text("""
                SELECT id_lid, Voornaam, Achternaam
                FROM lid
                WHERE gdpr_permission = 1
                ORDER BY achternaam_sort
            """))
            members = [dict(row._mapping) for row in result]

        return render_template("data_entry/media_manage.html",
                             performance=performance,
                             media_files=media_files,
                             members=members)
    except Exception as e:
        logger.error(f"Manage media error: {e}")
        flash("Kan media niet laden.", "danger")
        return redirect(url_for('data_entry.list_performances'))


@data_entry_bp.route("/performances/<ref_uitvoering>/media/upload", methods=["POST"])
@login_required
@admin_required
def upload_media(ref_uitvoering):
    """Upload media files for a performance"""
    try:
        config = Config.for_production()
        reader = KnaDataReader(config=config)

        # Get performance folder
        with reader.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT folder FROM uitvoering WHERE ref_uitvoering = :ref_uitvoering
            """), {'ref_uitvoering': ref_uitvoering})
            row = result.fetchone()
            if not row:
                flash("Voorstelling niet gevonden.", "danger")
                return redirect(url_for('data_entry.list_performances'))
            folder = row[0]

        files = request.files.getlist('files')
        type_media = request.form.get('type_media', 'foto')
        tagged_members = request.form.getlist('members')

        if not files or files[0].filename == '':
            flash('Geen bestanden geselecteerd.', 'warning')
            return redirect(url_for('data_entry.manage_media', ref_uitvoering=ref_uitvoering))

        # Create folder if it doesn't exist
        folder_path = Path(config.dir_resources) / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        uploaded_count = 0

        with reader.engine.connect() as conn:
            for file in files:
                if file and allowed_file(file.filename):
                    # Save file
                    filename = secure_filename(file.filename)
                    file_path = folder_path / filename
                    file.save(str(file_path))

                    # Get file extension
                    file_ext = filename.rsplit('.', 1)[1].lower()

                    # Add to database
                    conn.execute(text("""
                        INSERT INTO file (ref_uitvoering, bestand, type_media, file_ext, folder)
                        VALUES (:ref_uitvoering, :bestand, :type_media, :file_ext, :folder)
                    """), {
                        'ref_uitvoering': ref_uitvoering,
                        'bestand': filename,
                        'type_media': type_media,
                        'file_ext': file_ext,
                        'folder': folder
                    })

                    # Tag members
                    for member_id in tagged_members:
                        conn.execute(text("""
                            INSERT INTO file_leden (ref_uitvoering, bestand, lid, type_media, file_ext, folder, vlnr)
                            VALUES (:ref_uitvoering, :bestand, :lid, :type_media, :file_ext, :folder, '')
                        """), {
                            'ref_uitvoering': ref_uitvoering,
                            'bestand': filename,
                            'lid': member_id,
                            'type_media': type_media,
                            'file_ext': file_ext,
                            'folder': folder
                        })

                    uploaded_count += 1

            # Update media count
            conn.execute(text("""
                UPDATE uitvoering
                SET qty_media = (SELECT COUNT(*) FROM file WHERE ref_uitvoering = :ref_uitvoering)
                WHERE ref_uitvoering = :ref_uitvoering
            """), {'ref_uitvoering': ref_uitvoering})

            conn.commit()

        flash(f'{uploaded_count} bestand(en) geüpload!', 'success')

    except Exception as e:
        logger.error(f"Upload media error: {e}")
        flash(f'Fout bij uploaden: {str(e)}', 'danger')

    return redirect(url_for('data_entry.manage_media', ref_uitvoering=ref_uitvoering))
