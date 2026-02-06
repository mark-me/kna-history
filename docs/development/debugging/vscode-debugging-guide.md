![KNA Historie](../../images/code-ide.png){ align=right width="90" }

# VSCode Development Setup for KNA History

Complete guide to set up a local development environment with debugging for your Flask application.

## 🎯 What You'll Get

- ✅ Full Flask debugging with breakpoints
- ✅ Hot reload on code changes
- ✅ Local MariaDB database
- ✅ Database admin UI (Adminer)
- ✅ Python IntelliSense
- ✅ Jinja template support
- ✅ Git integration
- ✅ Auto-formatting

## 📋 Prerequisites

### Required
- **Python 3.13+** (`python --version`)
- **VSCode** (latest version)
- **Git**

### Recommended
- **uv** (fast Python package installer)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Docker** (for local database)

## 🚀 Quick Setup (5 Minutes)

### Step 1: Copy Files to Your Project

```bash
# Navigate to your project
cd /path/to/kna-history

# Copy VSCode configuration
cp -r /downloaded/vscode-debug/.vscode .

# Copy environment file
cp /downloaded/vscode-debug/.env.development .env

# Copy dev docker-compose
cp /downloaded/vscode-debug/docker-compose.dev.yml .

# Copy setup script
cp /downloaded/vscode-debug/setup-dev-environment.sh .
chmod +x setup-dev-environment.sh
```

### Step 2: Run Setup Script

```bash
./setup-dev-environment.sh
```

This will:
- Create virtual environment
- Install dependencies
- Start MariaDB container
- Configure VSCode

### Step 3: Open in VSCode

```bash
code .
```

### Step 4: Install Recommended Extensions

When VSCode opens, it will prompt you to install recommended extensions. Click **Install All**.

Or install manually:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Debugpy (ms-python.debugpy)

### Step 5: Load Test Data

```bash
# Activate virtual environment
source .venv/bin/activate

# Load your data
python -m kna_data.cli load --dev /path/to/kna_database.xlsx
```

### Step 6: Start Debugging!

Press **F5** (or click Run → Start Debugging)

Your app will start at: http://localhost:5000

## 🐛 Debugging Features

### Available Debug Configurations

Open the debug panel (Ctrl+Shift+D) and select from:

#### 1. **Python: Flask App** (Default)
- Runs Flask in debug mode
- Hot reload enabled
- Breakpoints work everywhere
- Template debugging enabled

#### 2. **Python: Current File**
- Debug any Python script
- Useful for testing individual modules

#### 3. **Python: Test Data Loader**
- Debug the data loading process
- Step through Excel import

#### 4. **Python: Attach to Docker**
- Attach debugger to running Docker container
- Advanced: requires container setup

### Using Breakpoints

1. **Set breakpoint**: Click left of line number (red dot appears)
2. **Trigger route**: Visit URL in browser
3. **Execution pauses**: VSCode shows variables, call stack
4. **Step through**: Use F10 (step over), F11 (step into)

Example:
```python
@app.route("/leden")
def view_leden():
    lst_leden = db_reader.leden()  # ← Set breakpoint here
    return render_template("leden.html", leden=lst_leden)
```

### Debug Console

While paused at breakpoint:
```python
# In Debug Console, you can execute code:
>>> len(lst_leden)
150
>>> lst_leden[0]
{'id_lid': 'ABC123', 'Voornaam': 'Jan', ...}
>>> db_reader.config.db_host
'127.0.0.1:3306'
```

### Watch Variables

Add variables to Watch panel:
- `lst_leden`
- `request.args`
- `session`
- `db_reader.engine`

## 📂 Project Structure

```
kna-history/
├── .vscode/
│   ├── launch.json          # Debug configurations
│   ├── settings.json        # Python/editor settings
│   └── extensions.json      # Recommended extensions
├── .venv/                   # Virtual environment
├── .env                     # Local environment variables
├── src/
│   ├── kna_data/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── reader.py
│   │   ├── loader.py
│   │   └── cli.py
│   ├── blueprints/
│   │   └── admin.py
│   ├── app.py
│   └── logging_kna.py
├── templates/
├── static/
├── tests/
├── docker-compose.dev.yml   # Local dev database
└── pyproject.toml
```

## 🗄️ Database Setup

### Local MariaDB Container

```bash
# Start database
docker compose -f docker-compose.dev.yml up -d

# Check status
docker compose -f docker-compose.dev.yml ps

# Stop database
docker compose -f docker-compose.dev.yml down

# Reset database (⚠️ destroys data)
docker compose -f docker-compose.dev.yml down -v
```

### Adminer (Database UI)

Access database via web interface:
- **URL**: http://localhost:8080
- **System**: MySQL
- **Server**: mariadb-dev
- **Username**: root
- **Password**: kna-toneel
- **Database**: kna

Features:
- Browse tables
- Run SQL queries
- Export/import data
- View table structure

### Direct Database Access

```bash
# Using Docker
docker compose -f docker-compose.dev.yml exec mariadb-dev mysql -u root -pkna-toneel kna

# Using MySQL client (if installed)
mysql -h 127.0.0.1 -u root -pkna-toneel kna
```

## 🔧 Configuration Files

### .vscode/launch.json

Defines debug configurations. Key environment variables:

```json
{
    "env": {
        "FLASK_APP": "src/app.py",
        "FLASK_DEBUG": "1",
        "MARIADB_HOST": "127.0.0.1:3306",
        "MARIADB_USER": "root",
        "MARIADB_PASSWORD": "kna-toneel",
        "MARIADB_DATABASE": "kna",
        "DIR_RESOURCES": "/data/kna_resources"
    }
}
```

### .vscode/settings.json

Python environment settings:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.envFile": "${workspaceFolder}/.env",
    "[python]": {
        "editor.formatOnSave": true
    }
}
```

### .env

Local environment variables (not committed to git):

```bash
FLASK_APP=src/app.py
FLASK_DEBUG=1
MARIADB_HOST=127.0.0.1:3306
DIR_RESOURCES=/data/kna_resources
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_reader.py

# In VSCode: Click flask icon in test explorer
```

### Debug Tests

1. Open test file
2. Click debug icon next to test function
3. Or set breakpoint and run test

## 📝 Common Tasks

### Start Development Server

**Option A: Debugger (Recommended)**
- Press F5
- Breakpoints work
- Auto-reload on changes

**Option B: Terminal**
```bash
source .venv/bin/activate
python src/app.py
```

### Load Data

```bash
source .venv/bin/activate
python -m kna_data.cli load --dev /path/to/kna_database.xlsx
```

### Run Single Script

```bash
source .venv/bin/activate
python src/kna_data/loader.py
```

### Format Code

```bash
# Auto-format on save (configured)
# Or manually:
black src/
```

### Check Code Quality

```bash
flake8 src/
```

## 🎨 Template Debugging

Jinja templates are debuggable!

1. Set breakpoint in Python view function
2. Inspect variables being passed to template
3. In Debug Console:
   ```python
   >>> render_template('leden.html', leden=lst_leden)
   ```

### Jinja Syntax Highlighting

`.vscode/settings.json` includes:
```json
{
    "files.associations": {
        "*.html": "jinja-html"
    }
}
```

## 🔍 Troubleshooting

### Virtual Environment Not Activated

**Problem**: Terminal shows system Python

**Solution**:
```bash
source .venv/bin/activate
```

Or set in VSCode: `Ctrl+Shift+P` → "Python: Select Interpreter" → `.venv/bin/python`

### Database Connection Failed

**Problem**: `Can't connect to MySQL server`

**Solution**:
```bash
# Check database is running
docker compose -f docker-compose.dev.yml ps

# Start if needed
docker compose -f docker-compose.dev.yml up -d

# Check .env has correct host
MARIADB_HOST=127.0.0.1:3306  # Not 'mariadb'
```

### Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'kna_data'`

**Solution**:
```bash
# Reinstall in editable mode
source .venv/bin/activate
pip install -e .
```

### Breakpoints Not Working

**Problem**: Breakpoints are gray or skipped

**Solution**:
1. Check "justMyCode" is false in launch.json
2. Ensure using VSCode debugger (F5), not terminal
3. Verify breakpoint is on executable line (not comment/blank)

### Port Already in Use

**Problem**: `Address already in use: 5000`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port in launch.json
"args": ["run", "--port=5001"]
```

## 🎓 Best Practices

### Code Organization

```python
# Use type hints
def view_leden() -> str:
    lst_leden: list[dict] = db_reader.leden()
    return render_template("leden.html", leden=lst_leden)

# Add docstrings
def view_leden() -> str:
    """Display list of all members."""
    ...
```

### Logging

```python
from logging_kna import logger

@app.route("/leden")
def view_leden():
    logger.info("Loading members list")
    lst_leden = db_reader.leden()
    logger.debug(f"Found {len(lst_leden)} members")
    return render_template("leden.html", leden=lst_leden)
```

### Configuration

Use environment-based config:

```python
from kna_data import Config

# Development
config = Config.for_development()

# Production
config = Config.for_production()
```

## 🚀 Advanced: Docker Container Debugging

To debug code running inside Docker:

### Step 1: Add debugpy to Container

Update `deploy/app/Dockerfile`:
```dockerfile
RUN uv pip install debugpy
```

### Step 2: Modify Container CMD

```dockerfile
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "gunicorn", ...]
```

### Step 3: Expose Port

In `docker-compose.yml`:
```yaml
ports:
  - "5000:5000"
  - "5678:5678"  # Debugpy
```

### Step 4: Attach Debugger

In VSCode, select: **Python: Attach to Docker**

## 📚 Resources

- [VSCode Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Flask Development](https://flask.palletsprojects.com/en/latest/debugging/)
- [debugpy Documentation](https://github.com/microsoft/debugpy)

## ✅ Checklist

Setup complete when you can:

- [ ] Open project in VSCode
- [ ] See recommended extensions installed
- [ ] Press F5 and Flask starts
- [ ] Visit http://localhost:5000
- [ ] Set breakpoint and it triggers
- [ ] Access database at http://localhost:8080
- [ ] Run tests from test explorer
- [ ] Code auto-formats on save
- [ ] IntelliSense works for imports

---

**Happy debugging! 🐛🔍**
