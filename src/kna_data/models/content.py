"""
KNA Content Reference Models

These are NOT ORM models - they're documentation only.
Tables are created and managed by services/loader.py using pandas.to_sql()

Stored in: kna database (SQLITE_KNA_PATH)
Managed by: pandas (not SQLAlchemy ORM)

Purpose:
- Document database schema
- Provide field references for queries
- Type hints and IDE support
"""


class ContentModel:
    """
    Base class for KNA content reference models.

    Not managed by SQLAlchemy - use pandas for all operations.
    """
    __tablename__ = None
    FIELDS = {}

    @classmethod
    def table_name(cls) -> str:
        """Get table name"""
        if not cls.__tablename__:
            raise ValueError(f"{cls.__name__} has no table name")
        return cls.__tablename__


class Lid(ContentModel):
    """
    Member (Lid) reference model.

    Represents theatre group members past and present.
    """
    __tablename__ = 'lid'

    FIELDS = {
        'id_lid': 'str',          # Primary key - unique member ID
        'Voornaam': 'str',        # First name
        'Achternaam': 'str',      # Last name (may include prefix like "van der")
        'achternaam_sort': 'str', # Computed - sortable last name
        'Geboortedatum': 'date',  # Birth date (optional)
        'Startjaar': 'int',       # Year joined KNA (optional)
        'gdpr_permission': 'int', # 1=visible in archive, 0=hidden
    }


class Uitvoering(ContentModel):
    """
    Performance (Uitvoering) reference model.

    Represents theatre performances and events.
    """
    __tablename__ = 'uitvoering'

    FIELDS = {
        'ref_uitvoering': 'str',  # Primary key - unique performance ID
        'titel': 'str',           # Performance title
        'auteur': 'str',          # Author/playwright
        'jaar': 'int',            # Year performed
        'type': 'str',            # Type: 'Uitvoering', 'Evenement', etc.
        'datum_van': 'date',      # Start date
        'datum_tot': 'date',      # End date
        'folder': 'str',          # Folder name for media files
        'regie': 'str',           # Director (enriched from roles)
        'qty_media': 'int',       # Number of media files (computed)
    }


class Rol(ContentModel):
    """
    Role reference model.

    Links members to performances with their roles.
    """
    __tablename__ = 'rol'

    FIELDS = {
        'id': 'int',              # Auto-increment primary key
        'ref_uitvoering': 'str',  # Foreign key → uitvoering
        'id_lid': 'str',          # Foreign key → lid
        'rol': 'str',             # Role name (e.g., "Hamlet", "Regie", "Decor")
        'rol_bijnaam': 'str',     # Role nickname/description (optional)
        'qty_media': 'int',       # Media count for this member-performance (computed)
    }


class File(ContentModel):
    """
    Media file reference model.

    Tracks photos, videos, PDFs, etc.
    """
    __tablename__ = 'file'

    FIELDS = {
        'id': 'int',              # Auto-increment primary key
        'ref_uitvoering': 'str',  # Foreign key → uitvoering
        'bestand': 'str',         # Filename
        'type_media': 'str',      # Media type: foto, poster, programma, artikel, video
        'file_ext': 'str',        # File extension (jpg, png, pdf, mp4)
        'folder': 'str',          # Folder path (copied from uitvoering)
    }


class FileLeden(ContentModel):
    """
    File-to-member mapping reference model.

    Links media files to the members appearing in them.
    """
    __tablename__ = 'file_leden'

    FIELDS = {
        'id': 'int',              # Auto-increment primary key
        'ref_uitvoering': 'str',  # Foreign key → uitvoering
        'bestand': 'str',         # Filename (FK → file)
        'lid': 'str',             # Foreign key → lid
        'type_media': 'str',      # Media type (copied from file)
        'file_ext': 'str',        # File extension (copied from file)
        'folder': 'str',          # Folder path (copied from file)
        'vlnr': 'str',            # Original column name from Excel
    }


class MediaType(ContentModel):
    """
    Media type lookup reference model.

    Defines available media categories.
    """
    __tablename__ = 'media_type'

    FIELDS = {
        'type_media': 'str',      # Primary key - media type code
        'beschrijving': 'str',    # Description/label
    }


# Model registry
CONTENT_MODELS = [
    Lid,
    Uitvoering,
    Rol,
    File,
    FileLeden,
    MediaType,
]


def get_kna_table_names() -> list[str]:
    """
    Get list of all KNA content table names.

    Returns:
        list: Table names in dependency order
    """
    return [model.table_name() for model in CONTENT_MODELS]


def get_model_by_table(table_name: str) -> type[ContentModel] | None:
    """
    Get model class by table name.

    Args:
        table_name: Name of table

    Returns:
        ContentModel subclass or None if not found
    """
    return next(
        (
            model
            for model in CONTENT_MODELS
            if model.table_name() == table_name
        ),
        None,
    )
