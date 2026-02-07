![Setup](../images/setup.png){ align=right width="90" }

# Development Setup

This guide helps you set up a local development environment for KNA History.

## 📋 Prerequisites

### Required Software

- **Python 3.13+**
- **MariaDB 10.11+** or MySQL 8.0+
- **Git**
- **uv** (Python package installer)

### Optional Tools

- **VS Code** with Python extension
- **Docker Desktop** (for container testing)
- **GitHub CLI** (`gh`) for workflow management

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/mark-me/kna-history.git
cd kna-history
```

### 2. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 3. Install Dependencies

```bash
# Install all dependencies
uv sync

# This creates a virtual environment and installs packages from pyproject.toml
```

### 4. Set Up MariaDB

#### Install MariaDB

=== "macOS"
    ```bash
    brew install mariadb
    brew services start mariadb
    ```

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install mariadb-server mariadb-client
    sudo systemctl start mariadb
    ```

=== "Windows"
    Download and install from [mariadb.org](https://mariadb.org/download/)

#### Create Databases

```bash
# Connect to MariaDB
mysql -u root -p

# In MySQL shell:
CREATE DATABASE kna;
CREATE DATABASE kna_users;
CREATE USER 'kna_dev'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON kna.* TO 'kna_dev'@'localhost';
GRANT ALL PRIVILEGES ON kna_users.* TO 'kna_dev'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment

Create `.env` file in project root:

```bash
cp env.example .env.local
```

Edit `.env.local`:

```bash
# Development configuration
FLASK_ENV=development
KNA_ENV=development

# Flask
SECRET_KEY=dev-secret-key-change-in-production
ADMIN_PASSWORD=admin123

# MariaDB (KNA Data)
MARIADB_HOST=127.0.0.1:3306
MARIADB_USER=kna_dev
MARIADB_PASSWORD=dev_password
MARIADB_DATABASE=kna

# Users Database (SQLite for development)
DATABASE_URL=sqlite:///dev.db

# Resources Directory
DIR_RESOURCES=./data/resources/
```

### 6. Create Resources Directory

```bash
mkdir -p data/resources
```

### 7. Initialize Database (Optional)

If you have sample Excel data:

```bash
# Validate Excel file
uv run -m kna_data.cli validate --dev path/to/sample_data.xlsx

# Load data
uv run -m kna_data.cli load --dev path/to/sample_data.xlsx
```

## ▶️ Running the Application

### Development Server

```bash
# Activate virtual environment (if not using uv run)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Run Flask development server
uv run -m src.app

# Or directly with Python
python src/app.py
```

Access at: `http://localhost:5000`

Default admin credentials:
- Username: `admin`
- Password: `admin123` (from ADMIN_PASSWORD in .env)

### With Auto-Reload

Flask development server has auto-reload enabled by default:

```python
if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, host="0.0.0.0", port=5000)
```

Changes to Python files automatically reload the server.

### CLI Commands

```bash
# Validate Excel file
uv run -m kna_data.cli validate --dev data.xlsx

# Load Excel data
uv run -m kna_data.cli load --dev data.xlsx

# Skip validation (faster, use with caution)
uv run -m kna_data.cli load --dev --skip-validation data.xlsx

# Generate thumbnails
uv run -m kna_data.cli thumbnails --dev
```

## 🔄 Development Workflow

### Code Style

We use standard Python tools:

```bash
# Install development tools
pip install black flake8 isort

# Format code
black src/

# Sort imports
isort src/

# Lint code
flake8 src/
```

### Pre-commit Checks

Before committing:

```bash
# Run formatters
black src/
isort src/

# Run linter
flake8 src/

# Run tests (if available)
pytest
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

## 🗂️ Project Structure

Understanding the codebase:

```bash
src/
├── kna_data/              # Core data package
│   ├── __init__.py       # Package exports
│   ├── config.py         # Configuration classes
│   ├── reader.py         # Database reader
│   ├── loader.py         # Excel data loader
│   ├── models.py         # SQLAlchemy models
│   └── cli.py            # CLI interface
│
├── blueprints/            # Flask blueprints
│   ├── admin.py          # Admin routes (/admin/*)
│   └── auth.py           # Auth routes (/auth/*)
│
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── admin/            # Admin templates
│   │   ├── dashboard.html
│   │   └── upload.html
│   └── ...
│
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── images/           # Images
│
├── app.py                 # Flask app factory
└── logging_kna.py         # Logging setup
```

## 🛠️ Configuration

### Development vs Production

The application uses different configs per environment:

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | True | False |
| `MARIADB_HOST` | 127.0.0.1:3306 | mariadb |
| `SQLALCHEMY_DATABASE_URI` | sqlite:///dev.db | mysql://... |
| `DIR_RESOURCES` | ./data/resources/ | /data/resources/ |

Environment is selected via `FLASK_ENV` or `KNA_ENV`:

```python
# Automatic
export FLASK_ENV=development
python src/app.py

# Explicit
app = create_app("development")
```

See [Configuration Guide](configuration.md) for details.

## 🗄️ Database Management

### View Database

```bash
# Connect to development database
mysql -u kna_dev -p kna

# Show tables
SHOW TABLES;

# Query data
SELECT * FROM lid LIMIT 10;
SELECT * FROM uitvoering ORDER BY jaar DESC;
```

### Reset Database

```bash
# Drop and recreate
mysql -u kna_dev -p -e "DROP DATABASE kna; CREATE DATABASE kna;"

# Reload from Excel
uv run -m kna_data.cli load --dev data.xlsx
```

### Migrations

Currently no migration system (tables are recreated on each load).

Future: Consider Alembic for schema migrations.

## 🐞 Debugging

### VS Code

See detailed guide: [VS Code Debugging](debugging/vscode-debugging-guide.md)

Quick setup in `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask: Development",
            "type": "python",
            "request": "launch",
            "module": "src.app",
            "env": {
                "FLASK_ENV": "development",
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "jinja": true
        }
    ]
}
```

### Print Debugging

```python
from logging_kna import logger

logger.info(f"Loading data from {file_path}")
logger.debug(f"Query result: {result}")
logger.error(f"Failed: {error}")
```

### Interactive Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or with IPython
import IPython; IPython.embed()
```

## 🧪 Testing

### Manual Testing

1. **Start dev server**
   ```bash
   uv run -m src.app
   ```

2. **Test endpoints**
   ```bash
   curl http://localhost:5000/health
   curl http://localhost:5000/
   ```

3. **Test admin functions**
   - Navigate to `/auth/login`
   - Login with admin credentials
   - Test upload at `/admin/upload`

### Automated Testing

Future: Add pytest tests

```python
# tests/test_loader.py
def test_validate_excel():
    loader = KnaDataLoader(config=DevelopmentConfig())
    result = loader.validate_excel("test_data.xlsx")
    assert result["valid"] == True
```

## ✅ Common Tasks

### Add New Route

1. **Create route in blueprint**
   ```python
   # src/blueprints/admin.py
   @admin_bp.route("/new-feature")
   def new_feature():
       return render_template("admin/new_feature.html")
   ```

2. **Create template**
   ```html
   <!-- src/templates/admin/new_feature.html -->
   {% extends "base.html" %}
   {% block content %}
   <h1>New Feature</h1>
   {% endblock %}
   ```

3. **Test locally**
   ```bash
   uv run -m src.app
   # Navigate to /admin/new-feature
   ```

### Add Database Column

1. **Update Excel structure** (add column to sheet)
2. **Update loader** to handle new column
3. **Reload data** from Excel

### Add Configuration Option

1. **Update config.py**
   ```python
   class Config:
       NEW_SETTING = os.getenv("NEW_SETTING", "default")
   ```

2. **Update env.example**
   ```bash
   NEW_SETTING=value
   ```

3. **Use in application**
   ```python
   from kna_data.config import get_config
   config = get_config()
   value = config.NEW_SETTING
   ```

## 🚑 Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'kna_data'"

**Solution**: Ensure PYTHONPATH is set:
```bash
export PYTHONPATH=$PWD/src
```

#### "Can't connect to MySQL server"

**Solution**: Check MariaDB is running:
```bash
# macOS
brew services list

# Linux
sudo systemctl status mariadb

# Start if needed
brew services start mariadb  # macOS
sudo systemctl start mariadb # Linux
```

#### "Database 'kna' doesn't exist"

**Solution**: Create database:
```bash
mysql -u root -p -e "CREATE DATABASE kna;"
```

#### "Permission denied on ./data/resources"

**Solution**: Fix permissions:
```bash
chmod -R 755 data/resources
```

### Getting Help

1. Check [Troubleshooting Guide](../deployment/troubleshooting.md)
2. Review [GitHub Issues](https://github.com/mark-me/kna-history/issues)
3. Create new issue with details

## 👣 Next Steps

- [Understand the architecture](architecture.md)
- [Learn about configuration](configuration.md)
- [Set up debugging](debugging/vscode-debugging-guide.md)
- [Explore the database schema](database.md)
- [Read API documentation](api-reference.md)
