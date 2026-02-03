## KNA Data Package

A Python package for managing KNA theatre group historical data, providing both data reading and loading capabilities.

### 📦 Package Structure

```
src/kna_data/
├── __init__.py          # Package exports
├── config.py            # Configuration management
├── reader.py            # Data reading (query database)
├── loader.py            # Data loading (ETL from Excel)
└── cli.py               # Command-line interface
```

### 🎯 Design Philosophy

**Separation of Concerns:**
- **Reader**: Read-only database access for web application
- **Loader**: Write operations for data import
- **Config**: Shared configuration for both

**Benefits:**
- Clean separation between read and write operations
- Independent testing of each component
- Different security requirements (reader=read-only, loader=write)
- Easy to swap loading mechanism (Excel → Web upload)

### 🚀 Usage

#### As a Library (in Flask app)

```python
from kna_data import Config, KnaDataReader

# Production (Docker)
config = Config.for_production()
reader = KnaDataReader(config=config)

# Get members
members = reader.leden()

# Get performances
performances = reader.voorstellingen()
```

#### Command-Line Interface

```bash
# Validate Excel file
python -m kna_data.cli validate /data/kna_resources/kna_database.xlsx

# Load data (production database)
python -m kna_data.cli load /data/kna_resources/kna_database.xlsx

# Load data (development/local database)
python -m kna_data.cli load --dev /path/to/kna_database.xlsx

# Skip validation (faster, but risky)
python -m kna_data.cli load --skip-validation /data/kna_resources/kna_database.xlsx

# Generate thumbnails only
python -m kna_data.cli thumbnails
```

#### As a Docker Command

```bash
# Load data in production container
docker compose exec kna-historie python -m kna_data.cli load /data/resources/kna_database.xlsx

# Validate file
docker compose exec kna-historie python -m kna_data.cli validate /data/resources/kna_database.xlsx
```

### 📊 Data Model

The package manages these database tables:

- **lid**: Members/actors
- **uitvoering**: Performances/productions
- **rol**: Roles (actors in performances)
- **file**: Media files (photos, videos, PDFs)
- **file_leden**: Media-to-member associations
- **media_type**: Types of media

### 🔧 Configuration

The `Config` class manages database and resource paths:

```python
from kna_data import Config

# Use environment variables (recommended)
config = Config()  # Reads from ENV vars

# Or specify explicitly
config = Config(
    db_host="mariadb",
    db_user="kna",
    db_password="password",
    db_name="kna",
    dir_resources="/data/resources/"
)

# Predefined configs
config = Config.for_production()   # Docker/production
config = Config.for_development()  # Local development
```

**Environment Variables:**
- `MARIADB_HOST` - Database host (default: `mariadb`)
- `MARIADB_USER` - Database user (default: `root`)
- `MARIADB_PASSWORD` - Database password
- `MARIADB_DATABASE` - Database name (default: `kna`)
- `DIR_RESOURCES` - Resources directory (default: `/data/resources/`)

### 📥 Data Loading Process

The `KnaDataLoader` performs ETL operations:

1. **Extract**: Read data from Excel file
2. **Transform**:
   - Clean and normalize data
   - Generate sortable surnames (handle Dutch prefixes)
   - Extract file extensions
   - Create media-to-member associations
3. **Load**: Write to database tables
4. **Post-process**: Generate image thumbnails

```python
from kna_data import Config, KnaDataLoader

loader = KnaDataLoader(config=Config.for_production())

# Validate before loading
validation = loader.validate_excel("/path/to/file.xlsx")
if validation["valid"]:
    stats = loader.load_from_excel("/path/to/file.xlsx")
    print(f"Loaded: {stats}")
```

### 📖 Data Reading

The `KnaDataReader` provides methods for querying data:

```python
from kna_data import Config, KnaDataReader

reader = KnaDataReader(config=Config.for_production())

# Get all members
members = reader.leden()

# Get member info
member = reader.lid_info(id_lid="ABC123")

# Get member media
media = reader.lid_media(id_lid="ABC123")

# Get all performances
performances = reader.voorstellingen()

# Get performance info
perf = reader.voorstelling_info(voorstelling="voorst_001")

# Get timeline
timeline = reader.timeline()
```

### 🔐 Security Considerations

**Reader (read-only):**
- Used by web application
- Only needs SELECT permissions
- Can run with restricted database user

**Loader (write access):**
- Used for data imports
- Needs CREATE, INSERT, UPDATE, DELETE permissions
- Should run with elevated privileges
- Should be protected (admin-only access)

### 🚧 Future: Web Upload Interface

The current CLI loader will be replaced/complemented with a web interface:

```python
# Future implementation
@app.route("/admin/upload", methods=["POST"])
def upload_data():
    file = request.files["excel_file"]
    
    loader = KnaDataLoader(config=config)
    
    # Validate
    validation = loader.validate_excel(file)
    if not validation["valid"]:
        return {"errors": validation["errors"]}, 400
    
    # Load
    stats = loader.load_from_excel(file)
    return {"success": True, "stats": stats}
```

### 🧪 Testing

```bash
# Test reader
python -m pytest tests/test_reader.py

# Test loader
python -m pytest tests/test_loader.py

# Test with development database
python -m pytest tests/ --dev
```

### 📝 Migration from Old Code

**Before:**
```python
# Old code
from data_reader import KnaDB

db = KnaDB(dir_resources="/data/resources/", debug=False)
members = db.leden()
```

**After:**
```python
# New code
from kna_data import Config, KnaDataReader

config = Config.for_production()
reader = KnaDataReader(config=config)
members = reader.leden()
```

**Changes:**
1. Class renamed: `KnaDB` → `KnaDataReader`
2. Configuration externalized to `Config` class
3. No more `debug` parameter (use `Config.for_development()`)
4. Import from package: `from kna_data import ...`

### 🎓 Best Practices

**For Web App:**
```python
# Initialize once at startup
from kna_data import Config, KnaDataReader

config = Config.for_production()
reader = KnaDataReader(config=config)

# Reuse reader instance
@app.route("/members")
def members():
    return reader.leden()
```

**For Data Loading:**
```python
# Use CLI for one-off loads
python -m kna_data.cli load /path/to/file.xlsx

# Or programmatically with validation
from kna_data import Config, KnaDataLoader

loader = KnaDataLoader(config=Config.for_production())

validation = loader.validate_excel(file_path)
if validation["valid"]:
    loader.load_from_excel(file_path)
else:
    handle_errors(validation["errors"])
```

### 🔄 Development Workflow

1. Make changes to Excel file
2. Validate: `python -m kna_data.cli validate file.xlsx`
3. Load locally: `python -m kna_data.cli load --dev file.xlsx`
4. Test web app locally
5. Load to production: `docker compose exec kna-historie python -m kna_data.cli load /data/resources/file.xlsx`

### 📚 API Reference

See individual module docstrings for detailed API documentation:

```python
help(KnaDataReader)
help(KnaDataLoader)
help(Config)
```

### 🐛 Troubleshooting

**Database connection errors:**
```bash
# Check environment variables
docker compose exec kna-historie env | grep MARIADB

# Test database connection
docker compose exec kna-historie python -c "from kna_data import Config; Config().get_engine().connect()"
```

**Excel validation failures:**
```bash
# Get detailed validation info
python -m kna_data.cli validate --verbose file.xlsx
```

**Thumbnail generation issues:**
```bash
# Check permissions
ls -la /data/resources/*/thumbnails

# Regenerate thumbnails
python -m kna_data.cli thumbnails
```
