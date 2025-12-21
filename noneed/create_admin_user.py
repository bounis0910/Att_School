#!/usr/bin/env python3
"""
Create admin user in PostgreSQL database
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash
from getpass import getpass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from urllib.parse import unquote

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

def main():
    print("\n" + "="*70)
    print("Create Admin User - PostgreSQL Attendance System")
    print("="*70 + "\n")
    
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL', '')
        if not DATABASE_URL:
            print("✗ DATABASE_URL not set in .env file")
            return 1
        
        # Get admin credentials
        username = input("Enter admin username: ").strip()
        if not username:
            print("✗ Username cannot be empty")
            return 1
        
        password = getpass("Enter admin password: ")
        if not password:
            print("✗ Password cannot be empty")
            return 1
        
        confirm_password = getpass("Confirm password: ")
        if password != confirm_password:
            print("✗ Passwords don't match")
            return 1
        
        # Connect to database
        params = parse_database_url(DATABASE_URL)
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM "user" WHERE username = %s', (username,))
        if cursor.fetchone():
            print(f"✗ User '{username}' already exists")
            cursor.close()
            conn.close()
            return 1
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert user
        cursor.execute(
            'INSERT INTO "user" (username, password, role) VALUES (%s, %s, %s)',
            (username, password_hash, 'admin')
        )
        conn.commit()
        
        print(f"\n✓ Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  Role: admin")
        print("\nYou can now login to the web interface with these credentials.\n")
        
        cursor.close()
        conn.close()
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
