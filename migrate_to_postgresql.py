#!/usr/bin/env python3
"""
Migration script: SQLite to PostgreSQL
Run this to migrate data from existing SQLite database to PostgreSQL
"""
import sqlite3
import asyncio
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = os.path.join(os.path.dirname(__file__), 'app.db')
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+asyncpg://user:password@localhost:5432/att_school'
)

# Convert async URL to sync URL for initial setup
SYNC_DATABASE_URL = DATABASE_URL.replace('asyncpg', 'psycopg2')

def create_postgresql_database():
    """Create PostgreSQL database if it doesn't exist"""
    # Connect to default postgres database
    postgres_url = SYNC_DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    try:
        conn = create_engine(postgres_url).connect()
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Check if database exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'att_school'"))
        if result.fetchone():
            print("Database att_school already exists")
            conn.close()
            return
        
        # Create database
        conn.execute(text("CREATE DATABASE att_school"))
        print("Created PostgreSQL database: att_school")
        conn.close()
    except Exception as e:
        print(f"Database creation failed: {e}")
        return False
    return True

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
    pg_engine = create_engine(SYNC_DATABASE_URL)
    pg_conn = pg_engine.connect()
    
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
            for row in rows:
                values = []
                for val in row:
                    if isinstance(val, str):
                        values.append(f"'{val.replace(chr(39), chr(39)*2)}'")  # Escape single quotes
                    elif val is None:
                        values.append("NULL")
                    else:
                        values.append(str(val))
                
                insert_stmt = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)}) ON CONFLICT DO NOTHING"
                try:
                    pg_conn.execute(text(insert_stmt))
                except Exception as e:
                    print(f"  Error inserting row: {e}")
            
            pg_conn.commit()
            print(f"  ✓ Migrated {len(rows)} rows")
        
        print("\nMigration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration error: {e}")
        pg_conn.rollback()
        return False
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

def create_indexes():
    """Create indexes on PostgreSQL"""
    print("\nCreating indexes...")
    
    pg_engine = create_engine(SYNC_DATABASE_URL)
    pg_conn = pg_engine.connect()
    
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
            pg_conn.execute(text(idx_stmt))
            print(f"  ✓ Created index: {idx_name}")
        
        pg_conn.commit()
        print("All indexes created successfully!")
        return True
    except Exception as e:
        print(f"Index creation error: {e}")
        pg_conn.rollback()
        return False
    finally:
        pg_conn.close()

if __name__ == '__main__':
    print("PostgreSQL Migration Tool")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_postgresql_database():
        print("Failed to create PostgreSQL database")
        exit(1)
    
    # Step 2: Migrate data
    if not migrate_data():
        print("Failed to migrate data")
        exit(1)
    
    # Step 3: Create indexes
    if not create_indexes():
        print("Failed to create indexes")
        exit(1)
    
    print("\n" + "=" * 50)
    print("Migration completed successfully!")
    print(f"Database URL: {DATABASE_URL}")
