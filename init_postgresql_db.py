#!/usr/bin/env python3
"""
Initialize PostgreSQL database for Attendance System
Uses psycopg2 directly - no SQLAlchemy
"""
import os
import sys
import psycopg2
from psycopg2 import sql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_connection():
    """Create PostgreSQL connection."""
    conn_string = os.environ.get('DATABASE_URL', '')
    if not conn_string:
        raise ValueError("DATABASE_URL not set in environment")
    # Remove asyncpg/psycopg2 driver prefixes if present
    conn_string = conn_string.replace('+asyncpg', '').replace('+psycopg2', '')
    print(f"Connecting to: {conn_string.split('@')[1] if '@' in conn_string else 'database'}")
    return psycopg2.connect(conn_string)

def init_database():
    """Initialize all tables and indexes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*70)
        print("PostgreSQL Database Initialization")
        print("="*70)
        
        # Create user table
        print("Creating 'user' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓")
        
        # Create school_class table
        print("Creating 'school_class' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_class (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                teacher_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES "user"(id) ON DELETE SET NULL
            )
        """)
        print("✓")
        
        # Create period table
        print("Creating 'period' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS period (
                id SERIAL PRIMARY KEY,
                period_num INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                start_time TIME,
                end_time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES school_class(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES "user"(id) ON DELETE CASCADE,
                UNIQUE(period_num, class_id, teacher_id)
            )
        """)
        print("✓")
        
        # Create student table
        print("Creating 'student' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                roll_number VARCHAR(20) UNIQUE NOT NULL,
                class_id INTEGER NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES school_class(id) ON DELETE CASCADE
            )
        """)
        print("✓")
        
        # Create subject table
        print("Creating 'subject' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(20) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓")
        
        # Create teacher_subject table
        print("Creating 'teacher_subject' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_subject (
                id SERIAL PRIMARY KEY,
                teacher_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES "user"(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subject(id) ON DELETE CASCADE,
                UNIQUE(teacher_id, subject_id)
            )
        """)
        print("✓")
        
        # Create attendance table with all required columns
        print("Creating 'attendance' table...", end=" ", flush=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                period INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'absent',
                remark VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES school_class(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES "user"(id) ON DELETE CASCADE,
                UNIQUE(student_id, date, period)
            )
        """)
        print("✓")
        
        # Create indexes for performance optimization
        print("\nCreating indexes...")
        
        indexes = [
            ("idx_attendance_date_class", 
             "CREATE INDEX IF NOT EXISTS idx_attendance_date_class ON attendance(date, class_id)"),
            
            ("idx_attendance_period_class_teacher",
             "CREATE INDEX IF NOT EXISTS idx_attendance_period_class_teacher ON attendance(period, class_id, teacher_id)"),
            
            ("idx_attendance_student_date",
             "CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date)"),
            
            ("idx_attendance_period",
             "CREATE INDEX IF NOT EXISTS idx_attendance_period ON attendance(period)"),
            
            ("idx_attendance_class_id",
             "CREATE INDEX IF NOT EXISTS idx_attendance_class_id ON attendance(class_id)"),
            
            ("idx_attendance_teacher_id",
             "CREATE INDEX IF NOT EXISTS idx_attendance_teacher_id ON attendance(teacher_id)"),
            
            ("idx_period_class_teacher",
             "CREATE INDEX IF NOT EXISTS idx_period_class_teacher ON period(class_id, teacher_id)"),
            
            ("idx_student_class",
             "CREATE INDEX IF NOT EXISTS idx_student_class ON student(class_id)"),
            
            ("idx_user_username",
             "CREATE INDEX IF NOT EXISTS idx_user_username ON \"user\"(username)"),
            
            ("idx_teacher_subject",
             "CREATE INDEX IF NOT EXISTS idx_teacher_subject ON teacher_subject(teacher_id, subject_id)"),
        ]
        
        for idx_name, idx_sql in indexes:
            print(f"  {idx_name}...", end=" ", flush=True)
            cursor.execute(idx_sql)
            print("✓")
        
        conn.commit()
        
        # Show table statistics
        print("\n" + "="*70)
        print("Table Statistics")
        print("="*70)
        
        tables = ['attendance', 'student', 'school_class', 'period', 'subject', '"user"']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} rows")
        
        # Show indexes
        print("\nIndexes on attendance table:")
        cursor.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'attendance' ORDER BY indexname
        """)
        
        indexes_list = cursor.fetchall()
        if indexes_list:
            for (idx,) in indexes_list:
                print(f"  - {idx}")
        else:
            print("  No indexes found")
        
        print("\n" + "="*70)
        print("✓ Database initialization completed successfully!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        success = init_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running: sudo systemctl status postgresql")
        print("  2. .env file is configured with DATABASE_URL")
        print("  3. Database and user 'adminit' are created")
        sys.exit(1)
