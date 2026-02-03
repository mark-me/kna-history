# Admin Blueprint - Web Upload Interface

Complete admin interface for uploading and managing KNA data via web interface.

## 🎯 Features

- ✅ **Drag-and-drop file upload** with visual feedback
- ✅ **Real-time validation** before loading
- ✅ **Progress indicators** showing current step
- ✅ **Database statistics** dashboard
- ✅ **Thumbnail regeneration** utility
- ✅ **Error handling** with clear messages
- ✅ **Session management** for multi-step process
- ✅ **Mobile responsive** design

## 📁 File Structure

```
src/
├── app.py                           # Updated with blueprint registration
└── blueprints/
    └── admin.py                     # Admin blueprint

templates/
├── base.html                        # Base template (reference)
└── admin/
    ├── dashboard.html               # Admin dashboard
    └── upload.html                  # Upload page
```

## 🚀 Quick Integration

### 1. Add Files to Your Project

```bash
# Copy blueprint
cp blueprints/admin.py /path/to/your/project/src/blueprints/

# Copy templates
cp -r templates/admin /path/to/your/project/templates/

# Update app.py
cp src/app.py /path/to/your/project/src/app.py
```

### 2. Create Blueprints Directory

```bash
mkdir -p /path/to/your/project/src/blueprints
touch /path/to/your/project/src/blueprints/__init__.py
```

### 3. Update Your Existing app.py

If you want to integrate into existing app.py instead of replacing:

```python
# Add these imports at the top
from blueprints.admin import admin_bp

# Configure session
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Register blueprint
app.register_blueprint(admin_bp)
```

### 4. Set Environment Variable

```bash
# In your .env file
FLASK_SECRET=your-secret-key-here  # Generate with: openssl rand -hex 32
```

## 🎨 URL Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/` | GET | Admin dashboard with statistics |
| `/admin/upload` | GET | Upload page |
| `/admin/upload/validate` | POST | Validate uploaded Excel file |
| `/admin/upload/load` | POST | Load validated data |
| `/admin/upload/cancel` | POST | Cancel upload and cleanup |
| `/admin/data/stats` | GET | Get database statistics (JSON) |
| `/admin/thumbnails/regenerate` | POST | Regenerate all thumbnails |

## 💡 How It Works

### Upload Flow

```
Step 1: Select File
    ↓
User drags/selects Excel file
    ↓
File validated client-side (type, size)
    ↓
Step 2: Server Validation
    ↓
POST to /admin/upload/validate
    ↓
Server checks:
  - File structure
  - Required sheets
  - Required columns
  - Row counts
    ↓
Validation results displayed
    ↓
Step 3: Load Data (if valid)
    ↓
POST to /admin/upload/load
    ↓
Server:
  - Loads data using KnaDataLoader
  - Generates thumbnails
  - Returns statistics
    ↓
Success message displayed
```

### Session Management

The blueprint uses Flask sessions to handle the multi-step process:

1. **Validate**: File saved to temp, path stored in session
2. **Load**: Uses temp file path from session
3. **Cancel**: Cleans up temp file and session

This prevents re-uploading the file for loading step.

## 🔒 Security Considerations

### File Upload Security

```python
# Implemented protections:
1. File extension validation (only .xlsx, .xls)
2. File size limit (50MB)
3. Secure filename sanitization
4. Temporary storage in /tmp
5. Immediate cleanup after processing
```

### Recommended Additions

```python
# TODO: Add authentication
from flask_login import login_required

@admin_bp.before_request
@login_required
def require_login():
    pass

# TODO: Add CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

## 📊 Dashboard Features

### Statistics Display

The dashboard shows real-time database statistics:

- Total members (leden)
- Total performances (voorstellingen)
- Total roles (rollen)
- Total media files
- Media breakdown by type

### Utilities

- **Upload Data**: Navigate to upload page
- **Regenerate Thumbnails**: Rebuild all thumbnail images

## 🎨 UI/UX Features

### Upload Page

**Drag & Drop:**
- Visual feedback on hover
- File info display after selection
- Clear/cancel option

**Progress Indicators:**
- 3-step progress bar
- Active step highlighting
- Clear visual state

**Validation Results:**
- ✅ Success: Green banner with details
- ❌ Error: Red banner with error list
- ⚠️ Warning: Yellow banner for warnings

**Loading Results:**
- Success: Statistics table
- Error: Detailed error message
- Return to dashboard link

### Responsive Design

- Mobile-friendly layout
- Touch-friendly drag & drop
- Adaptive grid layouts
- Proper spacing on all screens

## 🔧 Customization

### Change Upload Limits

```python
# In blueprints/admin.py

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}  # Add CSV
```

### Add Custom Validation

```python
# In kna_data/loader.py

def validate_excel(self, file_path: str) -> dict:
    validation = super().validate_excel(file_path)
    
    # Add custom validation
    df_leden = pd.read_excel(file_path, sheet_name="Leden")
    
    if df_leden['email'].isnull().any():
        validation['warnings'].append('Some members missing email')
    
    return validation
```

### Customize UI Colors

```html
<!-- In templates/admin/*.html -->

<!-- Change success color from green to blue -->
<div class="bg-blue-50 border-blue-200">
    <svg class="text-blue-400">...</svg>
</div>
```

## 🧪 Testing

### Manual Testing

```bash
# Start app
python src/app.py

# Navigate to http://localhost:5000/admin

# Test upload:
1. Click "Upload Data"
2. Drag/select test Excel file
3. Click "Valideer Bestand"
4. Review validation results
5. Click "Laad Data in Database"
6. Verify success message
```

### API Testing

```bash
# Test validation endpoint
curl -X POST \
  -F "file=@test_data.xlsx" \
  http://localhost:5000/admin/upload/validate

# Test stats endpoint
curl http://localhost:5000/admin/data/stats
```

## 📝 Example Usage

### Complete Upload Workflow

```
1. User navigates to /admin/upload

2. User drags Excel file to drop zone
   → JavaScript validates file type and size
   → File info displayed

3. User clicks "Valideer Bestand"
   → POST to /admin/upload/validate
   → File saved to /tmp/kna_uploads/20250202_143022_kna_database.xlsx
   → Validation runs
   → Results displayed
   → Temp path stored in session

4. User reviews validation (success)
   → Sees sheet counts
   → Sees any warnings

5. User clicks "Laad Data in Database"
   → POST to /admin/upload/load
   → Data loaded from temp file
   → Thumbnails generated
   → Temp file deleted
   → Session cleared
   → Statistics displayed

6. User clicks "Terug naar Dashboard"
   → Redirected to /admin/
   → Updated statistics visible
```

## 🐛 Troubleshooting

### Upload Fails

**File too large:**
```python
# Increase limit in app.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

**Invalid file type:**
```python
# Check ALLOWED_EXTENSIONS in blueprints/admin.py
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
```

### Validation Errors

**Missing sheets:**
- Ensure Excel has all required sheets: Leden, Uitvoering, Rollen, Bestand, Type_Media

**Missing columns:**
- Check Leden sheet has: id_lid, Voornaam, Achternaam

### Session Issues

**"No validated file found":**
- Sessions require SECRET_KEY to be set
- Check FLASK_SECRET in environment variables

```bash
# Set in .env
FLASK_SECRET=$(openssl rand -hex 32)
```

### Permissions

**Cannot write to /tmp:**
```python
# Change upload folder in blueprints/admin.py
UPLOAD_FOLDER = Path('/var/tmp/kna_uploads')
```

## 🔄 Migration from CLI

### Before (CLI)

```bash
# Manual upload to server
scp kna_database.xlsx server:/data/resources/

# SSH to server
ssh server

# Run load command
docker compose exec kna-historie python -m kna_data.cli load /data/resources/kna_database.xlsx
```

### After (Web Interface)

```
1. Navigate to https://your-domain.com/admin/upload
2. Drag file to browser
3. Click "Valideer Bestand"
4. Click "Laad Data in Database"
5. Done!
```

## 🎓 Best Practices

### For Production

1. **Add Authentication:**
   ```python
   from flask_login import login_required
   
   @admin_bp.before_request
   @login_required
   def check_auth():
       pass
   ```

2. **Add Logging:**
   ```python
   @admin_bp.after_request
   def log_upload(response):
       logger.info(f"Upload action: {request.endpoint}")
       return response
   ```

3. **Add Backup:**
   ```python
   def load_data():
       # Backup current database before loading
       backup_database()
       loader.load_from_excel(temp_path)
   ```

4. **Add Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app)
   
   @admin_bp.route('/upload/validate', methods=['POST'])
   @limiter.limit("5 per hour")
   def validate_upload():
       pass
   ```

### For Development

- Use `--dev` flag for local testing
- Test with various Excel files
- Check error handling
- Verify cleanup on errors

## 📚 API Reference

### POST /admin/upload/validate

**Request:**
```
Content-Type: multipart/form-data
file: [Excel file]
```

**Response (Success):**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "info": {
    "Leden": 150,
    "Uitvoering": 45,
    "Rollen": 380,
    "Bestand": 1200,
    "Type_Media": 5
  }
}
```

**Response (Error):**
```json
{
  "valid": false,
  "errors": [
    "Missing required sheet: Leden",
    "File too large"
  ],
  "warnings": []
}
```

### POST /admin/upload/load

**Response (Success):**
```json
{
  "success": true,
  "message": "Data loaded successfully from kna_database.xlsx",
  "stats": {
    "lid": 150,
    "uitvoering": 45,
    "rol": 380,
    "file": 1200,
    "file_leden": 3500,
    "media_type": 5,
    "thumbnails": 856
  }
}
```

## 🌟 Future Enhancements

- [ ] Add user authentication/authorization
- [ ] Add data versioning (keep history of loads)
- [ ] Add rollback capability
- [ ] Add preview of changes before loading
- [ ] Add incremental updates (not full replace)
- [ ] Add Excel template download
- [ ] Add data export functionality
- [ ] Add audit logging
- [ ] Add email notifications
- [ ] Add scheduled uploads

## ✅ Checklist

Before deploying to production:

- [ ] Set FLASK_SECRET environment variable
- [ ] Add authentication to admin routes
- [ ] Configure proper file upload limits
- [ ] Set up HTTPS for file uploads
- [ ] Test error handling thoroughly
- [ ] Add backup before load
- [ ] Configure proper logging
- [ ] Add CSRF protection
- [ ] Test on mobile devices
- [ ] Document admin user guide
