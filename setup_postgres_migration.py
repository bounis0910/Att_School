#!/usr/bin/env python3
"""
Setup PostgreSQL Attendance System
Complete setup from SQLite to PostgreSQL with sample data
"""
import os
import sys
import shutil
from pathlib import Path

def print_step(num, title):
    print(f"\n{'='*70}")
    print(f"Step {num}: {title}")
    print('='*70)

def backup_sqlite_app():
    """Backup original SQLite app.py"""
    print_step(1, "Backing Up SQLite Version")
    
    app_file = Path('app.py')
    backup_file = Path('app.py.bak.sqlite')
    
    if app_file.exists():
        shutil.copy(app_file, backup_file)
        print(f"✓ Backed up: app.py → app.py.bak.sqlite")
    else:
        print("⚠ app.py not found (may already be PostgreSQL version)")

def switch_to_postgresql():
    """Switch to PostgreSQL version"""
    print_step(2, "Switching to PostgreSQL Version")
    
    pg_app = Path('app_postgresql.py')
    app_file = Path('app.py')
    
    if pg_app.exists():
        shutil.copy(pg_app, app_file)
        print(f"✓ Switched: app_postgresql.py → app.py")
        print(f"✓ Your Flask app now uses PostgreSQL")
    else:
        print("✗ app_postgresql.py not found!")
        return False
    
    return True

def verify_database():
    """Verify PostgreSQL database connection"""
    print_step(3, "Verifying PostgreSQL Database")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        from urllib.parse import unquote
        
        load_dotenv()
        url = os.environ.get('DATABASE_URL', '')
        
        if not url:
            print("✗ DATABASE_URL not set in .env")
            return False
        
        # Parse URL
        url = url.replace('+asyncpg', '').replace('+psycopg2', '')
        url = url.replace('postgresql://', '')
        
        if '@' in url:
            creds, host_db = url.rsplit('@', 1)
            user, password = creds.split(':', 1)
            user = unquote(user)
            password = unquote(password)
        else:
            print("✗ Invalid DATABASE_URL format")
            return False
        
        if ':' in host_db:
            host, port_db = host_db.split(':')
            port, dbname = port_db.split('/', 1)
            port = int(port)
        else:
            host, dbname = host_db.split('/', 1)
            port = 5432
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        
        print(f"✓ Connected to PostgreSQL database: {dbname}")
        print(f"✓ Found {table_count} tables")
        
        # Show table summary
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' ORDER BY tablename
        """)
        tables = cursor.fetchall()
        print(f"✓ Tables: {', '.join([t[0] for t in tables])}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    print_step(4, "Checking Requirements")
    
    required = [
        'flask',
        'flask_login',
        'psycopg2',
        'python-dotenv',
        'werkzeug'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✓ {pkg}")
        except ImportError:
            print(f"✗ {pkg} (MISSING)")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def show_next_steps():
    """Show next steps"""
    print_step(5, "Setup Complete - Next Steps")
    
    steps = [
        ("Start Flask App", "python app.py"),
        ("Access Web UI", "Open http://localhost:5000 in browser"),
        ("Admin Login", "Username/password: Use those from your PostgreSQL database"),
        ("Run Load Test", "python load_test.py (benchmarks your system)"),
    ]
    
    for i, (desc, cmd) in enumerate(steps, 1):
        print(f"\n{i}. {desc}")
        print(f"   Command: {cmd}")

def main():
    print("\n" + "="*70)
    print("PostgreSQL Attendance System - Complete Setup")
    print("="*70)
    
    # Step 1: Backup
    backup_sqlite_app()
    
    # Step 2: Switch to PostgreSQL
    if not switch_to_postgresql():
        print("\n✗ Setup failed!")
        return 1
    
    # Step 3: Verify database
    if not verify_database():
        print("\n✗ Database verification failed!")
        return 1
    
    # Step 4: Check requirements
    if not check_requirements():
        print("\n⚠ Some requirements are missing (but app may still work)")
    
    # Step 5: Show next steps
    show_next_steps()
    
    print("\n" + "="*70)
    print("✓ Setup completed successfully!")
    print("="*70 + "\n")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
