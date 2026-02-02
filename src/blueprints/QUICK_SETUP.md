# Quick Setup: Admin Web Upload

## ⚡ 5-Minute Setup

### 1. Copy Files (1 minute)

```bash
# Navigate to your project
cd /path/to/kna-history

# Create blueprints directory
mkdir -p src/blueprints
touch src/blueprints/__init__.py

# Copy admin blueprint
cp /downloaded/blueprints/admin.py src/blueprints/

# Copy templates
cp -r /downloaded/templates/admin templates/
```

### 2. Update app.py (2 minutes)

Add these lines to your `src/app.py`:

```python
# At the top with other imports
from blueprints.admin import admin_bp

# After creating app
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Register blueprint
app.register_blueprint(admin_bp)
```

Or just replace your `app.py` with the provided one.

### 3. Set Environment Variable (1 minute)

```bash
# In your deploy/.env file, add:
FLASK_SECRET=your-secret-key-here

# Generate a secret key:
openssl rand -hex 32
```

### 4. Test Locally (1 minute)

```bash
# Start app
python src/app.py

# Open browser
http://localhost:5000/admin

# You should see the admin dashboard
```

## 🎯 What You Get

### Admin Dashboard (`/admin`)
- Database statistics
- Quick actions
- Media breakdown

### Upload Page (`/admin/upload`)
- Drag & drop file upload
- Real-time validation
- Progress indicators
- Clear error messages

### Features
- ✅ Replaces manual CLI uploads
- ✅ User-friendly interface
- ✅ Validation before loading
- ✅ Thumbnail regeneration
- ✅ Mobile responsive

## 📋 File Structure

After setup:

```
your-project/
├── src/
│   ├── app.py                    # ← Updated with blueprint
│   ├── blueprints/
│   │   ├── __init__.py
│   │   └── admin.py              # ← NEW
│   └── kna_data/
│       └── ...
├── templates/
│   ├── base.html                 # Your existing base
│   └── admin/                    # ← NEW
│       ├── dashboard.html
│       └── upload.html
└── deploy/
    └── .env                      # ← Add FLASK_SECRET
```

## 🚀 Usage

### Upload Data

1. Navigate to `http://your-domain.com/admin/upload`
2. Drag your Excel file or click to browse
3. Click "Valideer Bestand"
4. Review validation results
5. Click "Laad Data in Database"
6. Done!

### View Statistics

1. Navigate to `http://your-domain.com/admin`
2. See current database stats
3. Click "Regenereer Thumbnails" if needed

## 🔒 Security (Important!)

**For Production**, add authentication:

```python
# Simple example (use proper auth in production)
from functools import wraps
from flask import session, redirect, url_for

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Apply to blueprint
@admin_bp.before_request
@require_admin
def check_admin():
    pass
```

## 🐛 Troubleshooting

### "No module named 'blueprints'"

```bash
# Make sure __init__.py exists
touch src/blueprints/__init__.py
```

### "SECRET_KEY not set"

```bash
# Add to deploy/.env
FLASK_SECRET=$(openssl rand -hex 32)
```

### File upload fails

```python
# Increase size limit in app.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Cannot write to /tmp

```python
# Change in blueprints/admin.py
UPLOAD_FOLDER = Path('/var/tmp/kna_uploads')
```

## ✅ Checklist

Before going to production:

- [ ] Copied all files
- [ ] Updated app.py
- [ ] Set FLASK_SECRET in .env
- [ ] Tested locally
- [ ] Added authentication (recommended)
- [ ] Tested file upload
- [ ] Tested validation
- [ ] Tested data loading

## 📚 Documentation

- **ADMIN_BLUEPRINT.md** - Complete documentation
- **API reference** - See ADMIN_BLUEPRINT.md
- **Customization** - See ADMIN_BLUEPRINT.md

## 🎓 Next Steps

1. ✅ Setup complete - test it!
2. Add authentication for production
3. Customize UI colors/text if desired
4. Add backup before load (recommended)
5. Set up monitoring/logging

---

**Questions?** Check ADMIN_BLUEPRINT.md for detailed documentation!
