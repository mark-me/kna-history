#!/usr/bin/env python3
"""
Debug SQLite path resolution issue
"""

import os
import sys
from pathlib import Path


def debug_paths():
    """Debug exact paths being used"""
    print("="*60)
    print("PATH DEBUGGING")
    print("="*60)
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get paths from env
    kna_path = os.getenv('SQLITE_KNA_PATH', 'data/kna_dev.db')
    users_path = os.getenv('SQLITE_USERS_PATH', 'data/users_dev.db')
    
    print(f"\n1. ENVIRONMENT VARIABLES:")
    print(f"   SQLITE_KNA_PATH: {kna_path}")
    print(f"   SQLITE_USERS_PATH: {users_path}")
    
    # Current working directory
    cwd = Path.cwd()
    print(f"\n2. CURRENT WORKING DIRECTORY:")
    print(f"   {cwd}")
    
    # Resolve paths
    kna_resolved = Path(kna_path).resolve()
    users_resolved = Path(users_path).resolve()
    
    print(f"\n3. RESOLVED ABSOLUTE PATHS:")
    print(f"   KNA: {kna_resolved}")
    print(f"   Users: {users_resolved}")
    
    # Check if paths match what we expect
    kna_expected = cwd / "data" / "kna_dev.db"
    users_expected = cwd / "data" / "users_dev.db"
    
    print(f"\n4. EXPECTED PATHS:")
    print(f"   KNA: {kna_expected}")
    print(f"   Users: {users_expected}")
    
    print(f"\n5. DO THEY MATCH?")
    print(f"   KNA match: {kna_resolved == kna_expected}")
    print(f"   Users match: {users_resolved == users_expected}")
    
    # Check directory
    data_dir = Path("data")
    print(f"\n6. DATA DIRECTORY:")
    print(f"   Relative: {data_dir}")
    print(f"   Absolute: {data_dir.resolve()}")
    print(f"   Exists: {data_dir.exists()}")
    print(f"   Is directory: {data_dir.is_dir()}")
    
    # Try to create a test database
    print(f"\n7. TEST DATABASE CREATION:")
    
    test_db = data_dir / "test_direct.db"
    print(f"   Test file: {test_db}")
    print(f"   Absolute: {test_db.resolve()}")
    
    # Try with sqlite3 directly
    import sqlite3
    try:
        # Use absolute path
        conn = sqlite3.connect(str(test_db.resolve()))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        print(f"   ✅ Created with absolute path")
        test_db.unlink()
    except Exception as e:
        print(f"   ❌ Failed with absolute path: {e}")
    
    # Try with relative path
    try:
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        print(f"   ✅ Created with relative path")
        test_db.unlink()
    except Exception as e:
        print(f"   ❌ Failed with relative path: {e}")
    
    # Now test what Flask-SQLAlchemy will see
    print(f"\n8. FLASK-SQLALCHEMY URI:")
    
    # Build URI like config.py does
    uri_relative = f"sqlite:///{users_path}"
    uri_absolute = f"sqlite:///{users_resolved}"
    
    print(f"   Relative: {uri_relative}")
    print(f"   Absolute: {uri_absolute}")
    
    # Test with SQLAlchemy
    from sqlalchemy import create_engine, text
    
    print(f"\n9. SQLALCHEMY ENGINE TEST:")
    
    # Try relative
    try:
        engine = create_engine(uri_relative)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"   ✅ Relative URI works")
    except Exception as e:
        print(f"   ❌ Relative URI fails: {e}")
    
    # Try absolute
    try:
        engine = create_engine(uri_absolute)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"   ✅ Absolute URI works")
    except Exception as e:
        print(f"   ❌ Absolute URI fails: {e}")
    
    # Check what config.py actually creates
    print(f"\n10. CONFIG.PY ACTUAL URIS:")
    
    sys.path.insert(0, str(cwd))
    from kna_data.config import get_config
    
    config = get_config('development')
    print(f"   users_database_uri: {config.users_database_uri}")
    print(f"   kna_database_uri: {config.kna_database_uri}")
    
    # Try using those URIs
    print(f"\n11. TEST WITH CONFIG URIS:")
    
    try:
        engine = create_engine(config.users_database_uri)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"   ✅ Config users URI works")
    except Exception as e:
        print(f"   ❌ Config users URI fails: {e}")
    
    try:
        engine = create_engine(config.kna_database_uri)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"   ✅ Config KNA URI works")
    except Exception as e:
        print(f"   ❌ Config KNA URI fails: {e}")


if __name__ == '__main__':
    debug_paths()
