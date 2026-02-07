![Configuration](../images/configuration.png){ align=right width="90" }

# Configuration

This document provides detailed information about the KNA History configuration system.

## 🧭 Overview

The application uses a **unified configuration system** based on environment variables and configuration classes. This provides:

- ✅ **Environment-specific configs** (development, production, testing)
- ✅ **Single source of truth** via `.env` file
- ✅ **Type-safe configuration** with Python classes
- ✅ **Docker-friendly** environment variable substitution
- ✅ **Automatic environment detection**

## 🏗️ Configuration Architecture

### Configuration Classes

```python
# kna_data/config.py

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MiB

    # Database (MariaDB for KNA data)
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    MARIADB_USER = os.getenv("MARIADB_USER", "root")
    MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD")
    MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "kna")

    # Resources directory
    DIR_RESOURCES = os.getenv("DIR_RESOURCES", "/data/resources/")

class DevelopmentConfig(Config):
    """Development-specific settings"""
    DEBUG = True
    MARIADB_HOST = "127.0.0.1:3306"
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"

class ProductionConfig(Config):
    """Production-specific settings"""
    DEBUG = False
    MARIADB_HOST = os.getenv("MARIADB_HOST", "mariadb")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

class TestingConfig(Config):
    """Testing-specific settings"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

### Environment Selection

Configuration is selected automatically based on environment variables:

```python
def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("FLASK_ENV") or os.getenv("KNA_ENV", "production")

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "default": ProductionConfig
    }

    return config_map.get(env, config_map["default"])()
```

## 🌍 Environment Variables

### Core Variables

#### Application Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `production` | Environment name |
| `KNA_ENV` | No | `production` | Alternative to FLASK_ENV |
| `SECRET_KEY` | **Yes** | - | Flask secret for sessions/cookies |
| `ADMIN_PASSWORD` | **Yes** | - | Default admin user password |

#### MariaDB (KNA Data Database)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MARIADB_HOST` | No | `mariadb` | Database hostname |
| `MARIADB_USER` | No | `root` | Database username |
| `MARIADB_PASSWORD` | **Yes** | - | Database password |
| `MARIADB_DATABASE` | No | `kna` | Database name |
| `MARIADB_ROOT_PASSWORD` | **Yes** | - | Root password (for container) |

#### Users Database (Flask-Login)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | **Yes** | - | SQLAlchemy connection string |

#### File Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DIR_RESOURCES` | No | `/data/resources/` | Container path for media |
| `DIR_RESOURCES_HOST` | **Yes** | - | Host path (for Docker volume) |
| `DIR_MARIADB` | **Yes** | - | Host path for MariaDB data |

#### Domain & SSL

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOMAIN_NAME` | **Yes** | - | Domain for SSL certificates |
| `EMAIL_ADDRESS` | **Yes** | - | Email for Let's Encrypt |
| `DUCKDNS_SUBDOMAIN` | No | - | DuckDNS subdomain |
| `DUCKDNS_TOKEN` | No | - | DuckDNS API token |

### Environment Files

#### `.env` (Production)

```bash
# Environment
FLASK_ENV=production
KNA_ENV=production

# Flask
SECRET_KEY=<64-char-random-string>
ADMIN_PASSWORD=<strong-password>

# MariaDB (KNA Data)
MARIADB_HOST=mariadb
MARIADB_USER=kna
MARIADB_PASSWORD=<strong-password>
MARIADB_DATABASE=kna
MARIADB_ROOT_PASSWORD=<strong-password>

# Users Database
DATABASE_URL=mysql+mysqldb://kna:<password>@mariadb/kna_users

# File Storage
DIR_RESOURCES=/data/resources/
DIR_RESOURCES_HOST=/data/kna_resources
DIR_MARIADB=/data/mariadb

# Domain
DOMAIN_NAME=kna-historie.duckdns.org
EMAIL_ADDRESS=admin@example.com
```

#### `.env.local` (Development)

```bash
# Environment
FLASK_ENV=development
KNA_ENV=development

# Flask
SECRET_KEY=dev-secret-key-not-for-production
ADMIN_PASSWORD=admin123

# MariaDB (KNA Data)
MARIADB_HOST=127.0.0.1:3306
MARIADB_USER=root
MARIADB_PASSWORD=dev-password
MARIADB_DATABASE=kna

# Users Database (SQLite for dev)
DATABASE_URL=sqlite:///dev.db

# File Storage
DIR_RESOURCES=./data/resources/
```

## 🔧 Configuration Usage

### In Flask Application

```python
from kna_data.config import get_config

def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    # Configuration is now available
    app.config['SECRET_KEY']  # From config object
    app.config['DEBUG']       # True in development

    return app
```

### In CLI Tools

```python
from kna_data.config import get_config

def load_command(args):
    # Select environment
    env = "development" if args.dev else "production"
    config = get_config(env)

    # Use configuration
    loader = KnaDataLoader(config=config)
    loader.load_from_excel(args.file)
```

### In Data Components

```python
from kna_data.config import get_config

# Get configuration
config = get_config()

# Initialize reader with config
reader = KnaDataReader(config=config)

# Access settings
resources_dir = config.DIR_RESOURCES
db_engine = config.get_engine()
```

## 🗄️ Two-Database Design

The application uses **two separate databases**:

### 1. KNA Data Database (MariaDB)

**Purpose:** Historical theatre data

**Connection:**

```python
# Via config object
config = get_config()
engine = config.get_engine()

# Connection string
url = config.mariadb_url
# "mysql+mysqldb://kna:password@mariadb/kna"
```

**Tables:**

- `lid` - Members
- `uitvoering` - Performances
- `rol` - Roles
- `file` - Media files
- `file_leden` - File-member mapping
- `media_type` - Media types

**Used By:**

- `KnaDataReader` - Reading data
- `KnaDataLoader` - Loading from Excel
- `CLI tools` - Data management

### 2. Users Database (Configurable)

**Purpose:** Authentication and user management

**Connection:**

```python
# Via Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db.init_app(app)
```

**Options:**

=== "Production (MariaDB)"
    ```bash
    DATABASE_URL=mysql+mysqldb://kna:password@mariadb/kna_users
    ```

=== "Development (SQLite)"
    ```bash
    DATABASE_URL=sqlite:///dev.db
    ```

=== "Testing (In-Memory)"
    ```bash
    DATABASE_URL=sqlite:///:memory:
    ```

**Tables:**

- `users` - Application users

**Used By:**

- `Flask-Login` - Authentication
- `Admin blueprint` - User management

## 🧩 Configuration Properties

### Database URLs

#### MariaDB URL Property

```python
@property
def mariadb_url(self) -> str:
    """Construct MariaDB connection URL"""
    return (
        f"mysql+mysqldb://"
        f"{self.MARIADB_USER}:{self.MARIADB_PASSWORD}"
        f"@{self.MARIADB_HOST}/{self.MARIADB_DATABASE}"
    )
```

Usage:

```python
config = get_config()
print(config.mariadb_url)
# "mysql+mysqldb://kna:pass@mariadb/kna"
```

#### Users Database URL

```python
# Production
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    f"mysql+mysqldb://{MARIADB_USER}:{MARIADB_PASSWORD}@mariadb/kna_users"
)

# Development
SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"
```

### Engine Factory

```python
def get_engine(self):
    """Get SQLAlchemy engine for MariaDB"""
    return create_engine(
        self.mariadb_url,
        pool_pre_ping=True,      # Verify connections
        pool_recycle=3600,       # Recycle after 1 hour
        echo=self.DEBUG          # Log queries in debug mode
    )
```

## 🔀 Environment-Specific Behavior

### Development

**Features:**

- `DEBUG = True` - Flask debug mode
- Local MariaDB at `127.0.0.1:3306`
- SQLite for users (no setup needed)
- Auto-reload on code changes
- Detailed error pages
- Query logging enabled

**When to use:**

- Local development
- Testing changes
- Debugging issues

### Production

**Features:**

- `DEBUG = False` - No debug info
- MariaDB in Docker container
- MariaDB for users (persistent)
- Optimized for performance
- Generic error pages
- Minimal logging

**When to use:**

- Docker deployment
- Live server
- Production environment

### Testing

**Features:**

- `TESTING = True` - Test mode
- In-memory SQLite (fast, disposable)
- Clean state per test
- No external dependencies

**When to use:**

- Unit tests
- Integration tests
- CI/CD pipeline

## ✅ Configuration Validation

### Pre-Deployment Validation

Use the `validate-config.sh` script:

```bash
./validate-config.sh
```

**Checks:**

- ✅ All required variables present
- ✅ Strong passwords (not defaults)
- ✅ Valid database URLs
- ✅ Directories exist and writable
- ✅ No hardcoded secrets in code

### Runtime Validation

```python
def validate_config(config):
    """Validate configuration at runtime"""
    errors = []

    # Check required settings
    if not config.SECRET_KEY:
        errors.append("SECRET_KEY not set")

    if config.SECRET_KEY == "dev-secret-key":
        errors.append("Using default SECRET_KEY in production!")

    if not config.MARIADB_PASSWORD:
        errors.append("MARIADB_PASSWORD not set")

    # Check database connectivity
    try:
        engine = config.get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        errors.append(f"Database connection failed: {e}")

    return errors
```

## 🐳 Docker Configuration

### docker-compose.yml

Environment variables are passed from `.env` to containers:

```yaml
services:
  kna-historie:
    image: ghcr.io/mark-me/kna-history:latest
    environment:
      # Passed from .env file
      FLASK_ENV: ${FLASK_ENV:-production}
      SECRET_KEY: ${SECRET_KEY}
      MARIADB_HOST: ${MARIADB_HOST}
      MARIADB_USER: ${MARIADB_USER}
      MARIADB_PASSWORD: ${MARIADB_PASSWORD}
      MARIADB_DATABASE: ${MARIADB_DATABASE}
      DATABASE_URL: ${DATABASE_URL}
      DIR_RESOURCES: ${DIR_RESOURCES}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
    volumes:
      - resources:/data/resources

  mariadb:
    image: mariadb:10.11.6
    environment:
      MARIADB_ROOT_PASSWORD: ${MARIADB_ROOT_PASSWORD}
      MARIADB_DATABASE: ${MARIADB_DATABASE}
      MARIADB_USER: ${MARIADB_USER}
      MARIADB_PASSWORD: ${MARIADB_PASSWORD}
```

### Container Environment

Inside the container, configuration is accessed the same way:

```python
# Container automatically has environment variables
config = get_config()  # Reads FLASK_ENV, etc.
```

## 🧠 Advanced Configuration

### Custom Configuration Class

Create a custom config for special cases:

```python
class StagingConfig(ProductionConfig):
    """Staging environment configuration"""
    DEBUG = True  # Enable debug in staging
    SQLALCHEMY_ECHO = True  # Log all queries

# Register in config dict
config["staging"] = StagingConfig
```

Usage:

```bash
export FLASK_ENV=staging
python app.py
```

### Dynamic Configuration

Load additional settings from file:

```python
class Config:
    def __init__(self):
        self._load_from_env()
        self._load_from_file()

    def _load_from_file(self):
        """Load additional settings from JSON file"""
        config_file = os.getenv("CONFIG_FILE")
        if config_file and os.path.exists(config_file):
            with open(config_file) as f:
                data = json.load(f)
                for key, value in data.items():
                    setattr(self, key, value)
```

### Configuration Overrides

Override config for testing:

```python
def test_with_custom_config():
    # Temporarily override
    with patch.dict(os.environ, {
        'FLASK_ENV': 'testing',
        'SECRET_KEY': 'test-secret'
    }):
        config = get_config()
        assert config.TESTING == True
```

## 🔐 Security Considerations

### Secrets Management

**Never commit secrets:**

```gitignore
# .gitignore
.env
.env.local
.env.production
*.db
```

**Use strong secrets:**

```python
# Generate strong SECRET_KEY
import secrets
secret_key = secrets.token_urlsafe(48)
# "g8Kb9xvN3dP7mQ1wZ2fT4hL6jY8kR5sA0cV9bX3nM2uW1eR4t"
```

**Rotate secrets regularly:**

- Change `SECRET_KEY` every 90 days
- Rotate database passwords quarterly
- Update API tokens as needed

### Environment Isolation

**Separate environments:**

```bash
# Development
cp .env.example .env.local
# Edit with dev credentials

# Production
cp .env.example .env
# Edit with production credentials
```

**Different databases:**

- Dev: `kna_dev` database
- Staging: `kna_staging` database
- Production: `kna` database

## 🚑 Troubleshooting

### Common Issues

#### "Config not loading"

**Check:**

```python
import os
print(os.getenv("FLASK_ENV"))  # Should print environment
print(os.getenv("SECRET_KEY"))  # Should print key
```

**Fix:**

```bash
# Ensure .env file exists
ls -la .env

# Load manually if needed
export $(cat .env | xargs)
```

#### "Wrong configuration used"

**Debug:**

```python
config = get_config()
print(config.__class__.__name__)  # Should be DevelopmentConfig, etc.
print(config.DEBUG)  # True for dev, False for prod
```

**Fix:**

```bash
# Set environment explicitly
export FLASK_ENV=development
# Or
export KNA_ENV=production
```

#### "Database connection fails"

**Check URL:**

```python
config = get_config()
print(config.mariadb_url)
# Should be: mysql+mysqldb://user:pass@host/db
```

**Test connection:**

```python
try:
    engine = config.get_engine()
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## 📐 Best Practices

### Development

```bash
# Use .env.local for development
cp env.example .env.local

# Set environment
export FLASK_ENV=development

# Use development config explicitly in code
app = create_app("development")
```

### Production

```bash
# Use .env for production
cp env.example .env

# Generate strong secrets
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Validate before deploying
./validate-config.sh

# Set environment
export FLASK_ENV=production
```

### Testing

```python
# Use in-memory database for tests
def pytest_configure():
    os.environ['FLASK_ENV'] = 'testing'

def test_something():
    config = get_config()
    assert config.TESTING == True
    assert "memory" in config.SQLALCHEMY_DATABASE_URI
```

## 📘 Configuration Reference

Complete list of all configuration attributes:

### Base Config

```python
SECRET_KEY                    # Flask secret key
MAX_CONTENT_LENGTH           # Max upload size (bytes)
SQLALCHEMY_TRACK_MODIFICATIONS  # SQLAlchemy setting
MARIADB_HOST                 # Database hostname
MARIADB_USER                 # Database username
MARIADB_PASSWORD             # Database password
MARIADB_DATABASE             # Database name
DIR_RESOURCES                # Resources directory path
```

### Development Config

```python
DEBUG = True                 # Enable debug mode
MARIADB_HOST = "127.0.0.1:3306"  # Local database
SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"  # SQLite users DB
```

### Production Config

```python
DEBUG = False                # Disable debug
MARIADB_HOST = "mariadb"    # Docker service name
SQLALCHEMY_DATABASE_URI      # From DATABASE_URL env var
```

### Testing Config

```python
TESTING = True               # Enable test mode
MARIADB_HOST = "127.0.0.1:3306"  # Local database
SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory DB
```

## ➡️ Next Steps

- [Understand the architecture](architecture.md)
- [Review database schema](database.md)
- [Set up development environment](setup.md)
- [Deploy to production](../deployment/production.md)
