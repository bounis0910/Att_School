#!/usr/bin/env python3
"""
Load test script for PostgreSQL attendance system
Tests performance with bulk inserts, queries, and indexes
"""
import psycopg2
import time
import random
from datetime import datetime, timedelta
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_connection():
    """Create PostgreSQL connection."""
    conn_string = os.environ.get('DATABASE_URL', '').replace('+asyncpg', '')
    if not conn_string or 'postgresql' not in conn_string:
        raise ValueError("DATABASE_URL not set in environment")
    return psycopg2.connect(conn_string)

def test_query_by_date_class(conn, num_queries=100):
    """Test: Query attendance by date and class"""
    print(f"  Querying by date & class ({num_queries} queries)...", end=" ", flush=True)
    
    cursor = conn.cursor()
    start = time.time()
    
    for _ in range(num_queries):
        test_date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        class_id = random.randint(1, 10)
        
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = %s AND class_id = %s",
            (test_date, class_id)
        )
        cursor.fetchone()
    
    duration = time.time() - start
    rate = num_queries / duration
    print(f"✓ {duration*1000:.2f}ms ({rate:.0f} queries/sec)")
    cursor.close()
    return duration, rate

def test_query_by_period_class_teacher(conn, num_queries=100):
    """Test: Query by period, class_id, teacher_id (indexed columns)"""
    print(f"  Querying by period/class/teacher ({num_queries} queries)...", end=" ", flush=True)
    
    cursor = conn.cursor()
    start = time.time()
    
    for _ in range(num_queries):
        period = random.randint(10, 13)
        class_id = random.randint(1, 10)
        teacher_id = random.randint(1, 5)
        
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE period = %s AND class_id = %s AND teacher_id = %s",
            (period, class_id, teacher_id)
        )
        cursor.fetchone()
    
    duration = time.time() - start
    rate = num_queries / duration
    print(f"✓ {duration*1000:.2f}ms ({rate:.0f} queries/sec)")
    cursor.close()
    return duration, rate

def test_query_student_attendance(conn, num_queries=100):
    """Test: Query student attendance"""
    print(f"  Querying student attendance ({num_queries} queries)...", end=" ", flush=True)
    
    cursor = conn.cursor()
    start = time.time()
    
    for _ in range(num_queries):
        student_id = random.randint(1, 500)
        test_date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        
        cursor.execute(
            "SELECT * FROM attendance WHERE student_id = %s AND date = %s ORDER BY period",
            (student_id, test_date)
        )
        cursor.fetchall()
    
    duration = time.time() - start
    rate = num_queries / duration
    print(f"✓ {duration*1000:.2f}ms ({rate:.0f} queries/sec)")
    cursor.close()
    return duration, rate

def test_count_queries_dashboard(conn, num_queries=50):
    """Test: Multiple count queries (like staff dashboard)"""
    print(f"  Dashboard count queries ({num_queries} iterations)...", end=" ", flush=True)
    
    cursor = conn.cursor()
    start = time.time()
    
    for _ in range(num_queries):
        test_date = datetime.now().isoformat()
        class_id = random.randint(1, 10)
        period = random.randint(10, 13)
        
        # Multiple count queries per iteration
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = %s AND class_id = %s AND period = %s AND status = %s",
            (test_date, class_id, period, 'present')
        )
        cursor.fetchone()
        
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = %s AND class_id = %s AND period = %s AND status = %s AND (remark IS NULL OR remark != %s)",
            (test_date, class_id, period, 'absent', 'excused')
        )
        cursor.fetchone()
        
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = %s AND class_id = %s AND period = %s AND status = %s AND remark = %s",
            (test_date, class_id, period, 'absent', 'excused')
        )
        cursor.fetchone()
    
    duration = time.time() - start
    rate = (num_queries * 3) / duration
    print(f"✓ {duration*1000:.2f}ms ({rate:.0f} queries/sec)")
    cursor.close()
    return duration, rate

def test_distinct_periods(conn, num_queries=100):
    """Test: Get distinct periods"""
    print(f"  Distinct periods query ({num_queries} queries)...", end=" ", flush=True)
    
    cursor = conn.cursor()
    start = time.time()
    
    for _ in range(num_queries):
        test_date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        class_id = random.randint(1, 10)
        
        cursor.execute(
            "SELECT DISTINCT period FROM attendance WHERE date = %s AND class_id = %s ORDER BY period",
            (test_date, class_id)
        )
        cursor.fetchall()
    
    duration = time.time() - start
    rate = num_queries / duration
    print(f"✓ {duration*1000:.2f}ms ({rate:.0f} queries/sec)")
    cursor.close()
    return duration, rate

def show_table_stats(conn):
    """Show table statistics"""
    print("\nTable Statistics:")
    cursor = conn.cursor()
    
    tables = ['attendance', 'student', 'school_class', 'period', '"user"']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,} rows")
    
    cursor.close()

def show_indexes(conn):
    """Show index information"""
    print("\nIndexes on attendance table:")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT indexname FROM pg_indexes
        WHERE tablename = 'attendance' ORDER BY indexname
    """)
    
    indexes = cursor.fetchall()
    if indexes:
        for (index_name,) in indexes:
            print(f"  - {index_name}")
    else:
        print("  No indexes found")
    
    cursor.close()

def main():
    print("\n" + "="*70)
    print("PostgreSQL Attendance System - Load Test")
    print("="*70)
    
    try:
        conn = get_connection()
        print("✓ Connected to PostgreSQL\n")
        
        # Show stats
        show_table_stats(conn)
        show_indexes(conn)
        
        # Run tests
        print("\n" + "="*70)
        print("Performance Tests")
        print("="*70)
        
        results = {}
        
        results['date_class'] = test_query_by_date_class(conn, 200)
        results['period_class_teacher'] = test_query_by_period_class_teacher(conn, 200)
        results['student_attendance'] = test_query_student_attendance(conn, 100)
        results['dashboard_counts'] = test_count_queries_dashboard(conn, 100)
        results['distinct_periods'] = test_distinct_periods(conn, 100)
        
        # Summary
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)
        print(f"{'Test Name':<40} {'Duration':<15} {'Rate'}")
        print("-" * 70)
        
        for test_name, (duration, rate) in results.items():
            print(f"{test_name:<40} {duration*1000:>6.2f}ms        {rate:>6.0f}/sec")
        
        conn.close()
        
        print("\n✓ All tests completed successfully!\n")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running: sudo systemctl status postgresql")
        print("  2. .env file is configured with DATABASE_URL")
        print("  3. Database and user are created")
        return 1

if __name__ == '__main__':
    sys.exit(main())
