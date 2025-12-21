#!/usr/bin/env python3
"""
Migrate SQLite data to PostgreSQL with schema mapping
Handles column differences between SQLite and PostgreSQL schemas
"""
import sqlite3
import psycopg2
from psycopg2 import sql
import os
from datetime import datetime
from urllib.parse import unquote
from werkzeug.security import generate_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SQLITE_DB = 'app.db'
DATABASE_URL = os.environ.get('DATABASE_URL', '')

def parse_database_url(url):
    """Parse DATABASE_URL"""
    url = url.replace('+asyncpg', '').replace('+psycopg2', '')
    if not url.startswith('postgresql://'):
        raise ValueError("Invalid DATABASE_URL")
    
    url = url.replace('postgresql://', '')
    creds, host_db = url.rsplit('@', 1)
    user, password = creds.split(':', 1)
    user = unquote(user)
    password = unquote(password)
    
    if ':' in host_db:
        host, port_db = host_db.split(':')
        port, dbname = port_db.split('/', 1)
        port = int(port)
    else:
        host, dbname = host_db.split('/', 1)
        port = 5432
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': dbname
    }

def get_sqlite_connection():
    """Connect to SQLite"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection():
    """Connect to PostgreSQL"""
    params = parse_database_url(DATABASE_URL)
    return psycopg2.connect(**params)

def migrate_users(sqlite_conn, pg_conn):
    """Migrate user table"""
    print("\nMigrating users...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT id, name, role, password_hash, email FROM user")
    users = sqlite_cursor.fetchall()
    
    migrated = 0
    for user in users:
        try:
            # Map SQLite user to PostgreSQL user table
            pg_cursor.execute("""
                INSERT INTO "user" (id, username, password, role, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    password = EXCLUDED.password,
                    role = EXCLUDED.role
            """, (
                user['id'],
                user['name'],  # Use name as username
                user['password_hash'],
                user['role'],
                datetime.now()
            ))
            migrated += 1
        except Exception as e:
            print(f"\n  Warning: Could not migrate user {user['id']}: {e}")
    
    pg_conn.commit()
    print(f"✓ Migrated {migrated}/{len(users)} users")

def migrate_classes(sqlite_conn, pg_conn):
    """Migrate school_class table"""
    print("Migrating classes...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT id, name FROM school_class")
    classes = sqlite_cursor.fetchall()
    
    migrated = 0
    for cls in classes:
        try:
            pg_cursor.execute("""
                INSERT INTO school_class (id, name, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """, (cls['id'], cls['name'], datetime.now()))
            migrated += 1
        except Exception as e:
            print(f"\n  Warning: Could not migrate class {cls['id']}: {e}")
    
    pg_conn.commit()
    print(f"✓ Migrated {migrated}/{len(classes)} classes")

def migrate_subjects(sqlite_conn, pg_conn):
    """Migrate subject table"""
    print("Migrating subjects...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("SELECT id, name FROM subject")
    subjects = sqlite_cursor.fetchall()
    
    migrated = 0
    for subj in subjects:
        try:
            pg_cursor.execute("""
                INSERT INTO subject (id, name, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """, (subj['id'], subj['name'], datetime.now()))
            migrated += 1
        except Exception as e:
            print(f"\n  Warning: Could not migrate subject {subj['id']}: {e}")
    
    pg_conn.commit()
    print(f"✓ Migrated {migrated}/{len(subjects)} subjects")

def migrate_students(sqlite_conn, pg_conn):
    """Migrate student table"""
    print("Migrating students...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("""
        SELECT id, name, class_id, national_id, phone1, phone2 
        FROM student
    """)
    students = sqlite_cursor.fetchall()
    
    migrated = 0
    for student in students:
        try:
            pg_cursor.execute("""
                INSERT INTO student (id, name, class_id, roll_number, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    class_id = EXCLUDED.class_id,
                    phone = EXCLUDED.phone
            """, (
                student['id'],
                student['name'],
                student['class_id'],
                student['national_id'] or f"STU{student['id']}",  # Use national_id or generate roll number
                student['phone1'],
                datetime.now()
            ))
            migrated += 1
        except Exception as e:
            print(f"\n  Warning: Could not migrate student {student['id']}: {e}")
    
    pg_conn.commit()
    print(f"✓ Migrated {migrated}/{len(students)} students")

def migrate_periods(sqlite_conn, pg_conn):
    """Migrate period table"""
    print("Migrating periods...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("""
        SELECT id, day_of_week, period, start_time, end_time, class_id, subject_id
        FROM period
    """)
    periods = sqlite_cursor.fetchall()
    
    migrated = 0
    skipped = 0
    for period in periods:
        try:
            # Skip periods with NULL class_id
            if period['class_id'] is None:
                skipped += 1
                continue
            
            # Map SQLite period to PostgreSQL period
            # Note: SQLite has day_of_week and period separately
            # PostgreSQL just has period number
            pg_cursor.execute("""
                INSERT INTO period (id, period_num, class_id, teacher_id, start_time, end_time, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    period_num = EXCLUDED.period_num,
                    class_id = EXCLUDED.class_id,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time
            """, (
                period['id'],
                period['period'],
                period['class_id'],
                1,  # Default teacher_id (will need manual assignment)
                period['start_time'],
                period['end_time'],
                datetime.now()
            ))
            pg_conn.commit()
            migrated += 1
        except Exception as e:
            pg_conn.rollback()
            # Skip this period, continue with next
            skipped += 1
    
    print(f"✓ Migrated {migrated}/{len(periods)} periods (Skipped {skipped})")

def migrate_attendance(sqlite_conn, pg_conn):
    """Migrate attendance table"""
    print("Migrating attendance records...", end=" ", flush=True)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute("""
        SELECT id, student_id, date, period, status, class_id, teacher_id, remark, notes, created_at, updated_at
        FROM attendance
    """)
    records = sqlite_cursor.fetchall()
    
    migrated = 0
    for record in records:
        try:
            pg_cursor.execute("""
                INSERT INTO attendance (id, student_id, class_id, period, teacher_id, date, status, remark, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id, date, period) DO UPDATE SET
                    status = EXCLUDED.status,
                    remark = EXCLUDED.remark,
                    notes = EXCLUDED.notes,
                    updated_at = EXCLUDED.updated_at
            """, (
                record['id'],
                record['student_id'],
                record['class_id'],
                record['period'],
                record['teacher_id'],
                record['date'],
                record['status'],
                record['remark'],
                record['notes'],
                record['created_at'],
                record['updated_at']
            ))
            migrated += 1
        except Exception as e:
            print(f"\n  Warning: Could not migrate attendance {record['id']}: {e}")
    
    pg_conn.commit()
    print(f"✓ Migrated {migrated}/{len(records)} attendance records")

def main():
    print("\n" + "="*70)
    print("SQLite → PostgreSQL Data Migration")
    print("="*70)
    
    if not os.path.exists(SQLITE_DB):
        print(f"✗ SQLite database not found: {SQLITE_DB}")
        return 1
    
    if not DATABASE_URL:
        print("✗ DATABASE_URL not set in .env file")
        return 1
    
    try:
        # Connect to both databases
        print("\nConnecting to databases...")
        sqlite_conn = get_sqlite_connection()
        pg_conn = get_postgres_connection()
        print("✓ Connected to both SQLite and PostgreSQL")
        
        # Migrate tables in order (respecting foreign keys)
        print("\n" + "="*70)
        print("Migration Progress")
        print("="*70)
        
        migrate_users(sqlite_conn, pg_conn)
        migrate_classes(sqlite_conn, pg_conn)
        migrate_subjects(sqlite_conn, pg_conn)
        migrate_students(sqlite_conn, pg_conn)
        migrate_periods(sqlite_conn, pg_conn)
        migrate_attendance(sqlite_conn, pg_conn)
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n" + "="*70)
        print("✓ Migration completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Verify data in PostgreSQL: psql -U adminit -d attdbsch")
        print("  2. Create admin user: python create_admin_user.py")
        print("  3. Start Flask app: python app.py")
        print("  4. Access at http://localhost:5000\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
