![KNA Historie](../../images/code-ide.png){ align=right width="90" }

# VSCode Debugging - Quick Start

## ⚡ 5-Minute Setup

### 1. Copy Files (30 seconds)

```bash
cd /path/to/kna-history

# Copy all configuration
cp -r /downloaded/vscode-debug/.vscode .
cp /downloaded/vscode-debug/.env.development .env
cp /downloaded/vscode-debug/docker-compose.dev.yml .
cp /downloaded/vscode-debug/setup-dev-environment.sh .
chmod +x setup-dev-environment.sh
```

### 2. Run Setup Script (2 minutes)

```bash
./setup-dev-environment.sh
```

This automatically:
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Starts MariaDB database
- ✅ Sets up VSCode config

### 3. Open in VSCode (30 seconds)

```bash
code .
```

When prompted, install recommended extensions.

### 4. Load Test Data (1 minute)

```bash
source .venv/bin/activate
python -m kna_data.cli load --dev /path/to/kna_database.xlsx
```

### 5. Start Debugging! (10 seconds)

Press **F5**

Your app runs at: http://localhost:5000

---

## 🎯 What You Get

### Debugging Features
- ✅ **Set breakpoints** - Click left of line numbers
- ✅ **Inspect variables** - Hover over code
- ✅ **Debug console** - Execute code while paused
- ✅ **Call stack** - See function call hierarchy
- ✅ **Watch expressions** - Monitor specific variables
- ✅ **Hot reload** - Auto-restart on code changes

### Development Tools
- ✅ **Local database** - MariaDB on localhost:3306
- ✅ **DB admin UI** - Adminer at http://localhost:8080
- ✅ **IntelliSense** - Auto-complete for Python
- ✅ **Template support** - Jinja syntax highlighting
- ✅ **Auto-formatting** - Black on save
- ✅ **Linting** - Flake8 error checking

---

## 🐛 Using the Debugger

### Set a Breakpoint

1. Open `src/app.py`
2. Find this function:
   ```python
   @app.route("/leden")
   def view_leden():
       lst_leden = db_reader.leden()  # ← Click here
       return render_template("leden.html", leden=lst_leden)
   ```
3. Click left of line number (red dot appears)
4. Press **F5** to start debugging
5. Visit http://localhost:5000/leden in browser
6. Code pauses at breakpoint!

### Inspect Variables

While paused:
- **Hover** over variables to see values
- Check **Variables** panel on left
- Use **Debug Console** at bottom:
  ```python
  >>> len(lst_leden)
  150
  >>> lst_leden[0]['Voornaam']
  'Jan'
  ```

### Step Through Code

- **F10** - Step over (next line)
- **F11** - Step into (enter function)
- **F5** - Continue
- **Shift+F5** - Stop

---

## 🗄️ Database Access

### Adminer (Web UI)
- **URL**: http://localhost:8080
- **Server**: mariadb-dev
- **Username**: root
- **Password**: kna-toneel
- **Database**: kna

### Command Line
```bash
docker compose -f docker-compose.dev.yml exec mariadb-dev mysql -u root -pkna-toneel kna
```

---

## 🎨 Available Debug Configs

Press **F5** and select:

| Config | Purpose |
|--------|---------|
| **Python: Flask App** | Main app debugging (default) |
| **Python: Current File** | Run any Python script |
| **Python: Test Data Loader** | Debug data loading |
| **Python: Attach to Docker** | Debug in container |

---

## 📁 File Structure

```
kna-history/
├── .vscode/
│   ├── launch.json          # ← Debug configurations
│   ├── settings.json        # ← Python settings
│   └── extensions.json      # ← Recommended extensions
├── .env                     # ← Your local config
├── .venv/                   # ← Virtual environment
├── docker-compose.dev.yml   # ← Local database
└── src/
    └── app.py
```

---

## 🔧 Customize Settings

### Change Database Port

Edit `.env`:
```bash
MARIADB_HOST=127.0.0.1:3307  # Use port 3307
```

Edit `docker-compose.dev.yml`:
```yaml
ports:
  - "3307:3306"  # Map to 3307
```

### Change Flask Port

Edit `.vscode/launch.json`:
```json
"args": [
    "run",
    "--port=5001"  # Use port 5001
]
```

### Change Data Directory

Edit `.env`:
```bash
DIR_RESOURCES=/your/custom/path
```

---

## 🆘 Troubleshooting

### "Module not found: kna_data"
```bash
source .venv/bin/activate
pip install -e .
```

### "Can't connect to database"
```bash
# Start database
docker compose -f docker-compose.dev.yml up -d

# Check it's running
docker compose -f docker-compose.dev.yml ps
```

### "Port 5000 already in use"
```bash
# Find and kill process
lsof -i :5000
kill -9 <PID>
```

### Breakpoints not working
1. Make sure you pressed **F5** (not just `python app.py`)
2. Check `.vscode/launch.json` exists
3. Verify breakpoint is on executable line (not blank/comment)

---

## ✅ Success Checklist

You're ready when:

- [ ] Press F5 and Flask starts
- [ ] Visit http://localhost:5000 and see app
- [ ] Set breakpoint and it pauses
- [ ] Variables panel shows data
- [ ] Access database at http://localhost:8080
- [ ] Code auto-formats on save
- [ ] IntelliSense suggests completions

---

## 📚 Full Documentation

See **VSCODE_DEBUGGING_GUIDE.md** for:
- Advanced debugging techniques
- Testing setup
- Docker container debugging
- Best practices
- Complete troubleshooting guide

---

**That's it! Press F5 and start debugging! 🐛✨**
