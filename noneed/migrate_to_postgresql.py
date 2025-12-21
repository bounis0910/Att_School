#!/usr/bin/env python3
"""
Migration script: SQLite to PostgreSQL
Uses psycopg2 directly (no SQLAlchemy)
Migrates data from existing SQLite database to PostgreSQL
"""
import sqlite3
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

SQLITE_DB = os.path.join(os.path.dirname(__file__), 'app.db')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

def parse_database_url(url):
    """Parse DATABASE_URL to get connection parameters"""
    # Remove asyncpg/psycopg2 driver prefixes if present
    url = url.replace('+asyncpg', '').replace('+psycopg2', '')
    
    # Parse: postgresql://user:password@host:port/dbname
    if not url.startswith('postgresql://'):
        raise ValueError("Invalid DATABASE_URL format")
    
    url = url.replace('postgresql://', '')
    
    # Split credentials and host
    if '@' in url:
        creds, host_db = url.rsplit('@', 1)  # Use rsplit to handle @ in password
        user, password = creds.split(':', 1)  # Use split with maxsplit=1 to handle : in password
        # Decode URL-encoded characters
        user = unquote(user)
        password = unquote(password)
    else:
        raise ValueError("DATABASE_URL must include credentials")
    
    # Split host and database
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

def get_pg_connection():
    """Create PostgreSQL connection"""
    try:
        params = parse_database_url(DATABASE_URL)
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return None

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    if not os.path.exists(SQLITE_DB):
        print(f"SQLite database not found: {SQLITE_DB}")
        return False
    
    print("Starting migration from SQLite to PostgreSQL...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = get_pg_connection()
    if not pg_conn:
        sqlite_conn.close()
        return False
    
    pg_cursor = pg_conn.cursor()
    
    try:
        # Get all tables
        sqlite_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        for table in tables:
            print(f"Migrating table: {table}")
            
            # Get all rows from SQLite table
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  - Table {table} is empty")
                continue
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Insert into PostgreSQL
            migrated = 0
            for row in rows:
                # Build INSERT statement with proper parameterization
                placeholders = ', '.join(['%s'] * len(columns))
                insert_stmt = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                # Convert row values to list
                values = []
                for val in row:
                    values.append(val)
                
                try:
                    pg_cursor.execute(insert_stmt, values)
                    migrated += 1
                except psycopg2.errors.ForeignKeyViolation as e:
                    # Skip rows with foreign key violations (dependent data may not exist yet)
                    print(f"  - Skipped row due to FK constraint: {e}")
                except Exception as e:
                    print(f"  - Error inserting row: {e}")
            
            pg_conn.commit()
            print(f"  ✓ Migrated {migrated} rows")
        
        print("\n✓ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration error: {e}")
        pg_conn.rollback()
        return False
    
    finally:
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()

def create_indexes():
    """Create indexes on PostgreSQL"""
    print("\nCreating indexes...")
    
    pg_conn = get_pg_connection()
    if not pg_conn:
        return False
    
    pg_cursor = pg_conn.cursor()
    
    indexes = [
        ("idx_attendance_period_class_teacher", 
         "CREATE INDEX IF NOT EXISTS idx_attendance_period_class_teacher ON attendance(period, class_id, teacher_id)"),
        ("idx_attendance_student_date_period",
         "CREATE INDEX IF NOT EXISTS idx_attendance_student_date_period ON attendance(student_id, date, period)"),
        ("idx_attendance_date_class",
         "CREATE INDEX IF NOT EXISTS idx_attendance_date_class ON attendance(date, class_id)"),
        ("idx_student_class",
         "CREATE INDEX IF NOT EXISTS idx_student_class ON student(class_id)"),
    ]
    
    try:
        for idx_name, idx_stmt in indexes:
            pg_cursor.execute(idx_stmt)
            print(f"  ✓ Created index: {idx_name}")
        
        pg_conn.commit()
        print("✓ All indexes created successfully!")
        return True
    except Exception as e:
        print(f"Index creation error: {e}")
        pg_conn.rollback()
        return False
    finally:
        pg_cursor.close()
        pg_conn.close()

if __name__ == '__main__':
    print("PostgreSQL Migration Tool")
    print("=" * 70)
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set in .env file")
        exit(1)
    
    # Step 1: Check database connection
    pg_conn = get_pg_connection()
    if pg_conn:
        print("✓ Connected to PostgreSQL database")
        pg_conn.close()
    else:
        print("ERROR: Could not connect to PostgreSQL database")
        exit(1)
    
    # Step 2: Migrate data
    if os.path.exists(SQLITE_DB):
        if not migrate_data():
            print("Failed to migrate data")
            exit(1)
    else:
        print(f"Skipping data migration (SQLite DB not found: {SQLITE_DB})")
    
    # Step 3: Create indexes
    if not create_indexes():
        print("Failed to create indexes")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✓ Migration completed successfully!")
    print("=" * 70 + "\n")
