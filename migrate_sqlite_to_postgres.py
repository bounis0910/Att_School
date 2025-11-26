#!/usr/bin/env python3
"""
Migration script: SQLite to PostgreSQL
Migrates all data from SQLite to PostgreSQL
"""
import sqlite3
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import argparse
from datetime import datetime

load_dotenv()

def get_sqlite_data(sqlite_path):
    """Load all data from SQLite database."""
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        data[table] = [dict(row) for row in rows]
        print(f"  {table}: {len(rows)} records")
    
    conn.close()
    return data

def migrate_to_postgresql(data, pg_conn_string):
    """Migrate data to PostgreSQL."""
    conn = psycopg2.connect(pg_conn_string)
    cursor = conn.cursor()
    
    print("\nMigrating data to PostgreSQL...")
    
    # Disable foreign key checks temporarily
    cursor.execute("SET CONSTRAINTS ALL DEFERRED")
    
    for table_name, rows in data.items():
        if not rows:
            print(f"  {table_name}: skipped (no data)")
            continue
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Handle SQLite table names with quotes if needed
        safe_table = f'"{table_name}"' if table_name == 'user' else table_name
        
        # Build insert statement
        placeholders = ','.join(['%s'] * len(columns))
        col_names = ','.join([f'"{col}"' if col in ['user'] else col for col in columns])
        
        insert_sql = f"INSERT INTO {safe_table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        # Insert rows
        migrated = 0
        for row in rows:
            values = [row.get(col) for col in columns]
            try:
                cursor.execute(insert_sql, values)
                migrated += 1
            except Exception as e:
                print(f"    Error inserting into {table_name}: {e}")
                continue
        
        conn.commit()
        print(f"  {table_name}: {migrated} records migrated")
    
    # Re-enable foreign key checks
    cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\nMigration completed!")

def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite database to PostgreSQL')
    parser.add_argument('--sqlite', default='app.db', help='Path to SQLite database')
    parser.add_argument('--postgres', default=None, help='PostgreSQL connection string')
    
    args = parser.parse_args()
    
    # Get connection string
    pg_conn_string = args.postgres or os.environ.get('DATABASE_URL', '').replace('+asyncpg', '')
    
    if not pg_conn_string or 'postgresql' not in pg_conn_string:
        print("Error: PostgreSQL connection string not found!")
        print("Set DATABASE_URL in .env or use --postgres argument")
        return
    
    if not os.path.exists(args.sqlite):
        print(f"Error: SQLite database not found at {args.sqlite}")
        return
    
    print(f"Starting migration from SQLite ({args.sqlite}) to PostgreSQL...")
    print(f"PostgreSQL: {pg_conn_string.split('@')[1] if '@' in pg_conn_string else 'unknown'}")
    
    try:
        # Load SQLite data
        print("\nReading from SQLite...")
        data = get_sqlite_data(args.sqlite)
        
        # Migrate to PostgreSQL
        migrate_to_postgresql(data, pg_conn_string)
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
