"""
KNA Data Models

SQLAlchemy models for both user authentication and KNA historical data.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ============================================================================
# User Authentication Models (for Flask-Login)
# ============================================================================

class User(db.Model, UserMixin):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)  # admin / viewer
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    # Required by Flask-Login
    @property
    def is_active(self):
        """Check if user account is active"""
        return self.active
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================================
# KNA Historical Data Models
# ============================================================================
# Note: These tables are managed by loader.py using pandas.to_sql()
# The models below are for reference and potential future ORM usage
# ============================================================================

class Lid(db.Model):
    """Member (Lid) model - For reference only, loaded via pandas"""
    __tablename__ = 'lid'
    
    id_lid = db.Column(db.String(50), primary_key=True)
    Voornaam = db.Column(db.String(100))
    Achternaam = db.Column(db.String(100))
    achternaam_sort = db.Column(db.String(150))
    Geboortedatum = db.Column(db.Date)
    Startjaar = db.Column(db.Integer)
    gdpr_permission = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<Lid {self.Voornaam} {self.Achternaam}>'


class Uitvoering(db.Model):
    """Performance (Uitvoering) model - For reference only, loaded via pandas"""
    __tablename__ = 'uitvoering'
    
    ref_uitvoering = db.Column(db.String(100), primary_key=True)
    titel = db.Column(db.String(200))
    auteur = db.Column(db.String(200))
    jaar = db.Column(db.Integer)
    type = db.Column(db.String(50))  # 'Uitvoering', 'Evenement', etc.
    datum_van = db.Column(db.Date)
    datum_tot = db.Column(db.Date)
    folder = db.Column(db.String(200))
    regie = db.Column(db.String(100))
    qty_media = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Uitvoering {self.titel} ({self.jaar})>'


class Rol(db.Model):
    """Role model - For reference only, loaded via pandas"""
    __tablename__ = 'rol'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref_uitvoering = db.Column(db.String(100))
    id_lid = db.Column(db.String(50))
    rol = db.Column(db.String(100))
    rol_bijnaam = db.Column(db.String(100))
    qty_media = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Rol {self.rol} in {self.ref_uitvoering}>'


class File(db.Model):
    """Media file model - For reference only, loaded via pandas"""
    __tablename__ = 'file'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref_uitvoering = db.Column(db.String(100))
    bestand = db.Column(db.String(255))
    type_media = db.Column(db.String(50))
    file_ext = db.Column(db.String(10))
    folder = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<File {self.bestand}>'


class FileLeden(db.Model):
    """File-to-member mapping - For reference only, loaded via pandas"""
    __tablename__ = 'file_leden'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref_uitvoering = db.Column(db.String(100))
    bestand = db.Column(db.String(255))
    lid = db.Column(db.String(50))
    type_media = db.Column(db.String(50))
    file_ext = db.Column(db.String(10))
    folder = db.Column(db.String(200))
    vlnr = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<FileLeden {self.bestand} - {self.lid}>'


class MediaType(db.Model):
    """Media type lookup - For reference only, loaded via pandas"""
    __tablename__ = 'media_type'
    
    type_media = db.Column(db.String(50), primary_key=True)
    beschrijving = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<MediaType {self.type_media}>'
