#!/usr/bin/env python3
"""Test attendance save functionality"""
import requests
from datetime import datetime
import psycopg2
from urllib.parse import unquote

# Database connection
DATABASE_URL = 'postgresql://adminit:Bel@1981@localhost:5432/attdbsch'
url = DATABASE_URL.replace('postgresql://', '')

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

db_params = {'host': host, 'port': port, 'user': user, 'password': password, 'database': dbname}

# Test data
BASE_URL = 'http://localhost:5000'

print("=" * 50)
print("TESTING ATTENDANCE SAVE FUNCTIONALITY")
print("=" * 50)

# Get attendance page
print("\n1. Getting attendance page...")
response = requests.get(f"{BASE_URL}/attendance-tabs")
print(f"   Status: {response.status_code}")

# Extract form data from page (simplified - just test with known values)
class_id = 1  # We know class 1 exists
teacher_id = 86  # We know teacher 86 exists (اشرف محمود محمد احمد)
student_id = 1  # We know student 1 exists
period = 1  # Period 1

print(f"\n2. Submitting attendance data...")
print(f"   Class: {class_id}")
print(f"   Teacher: {teacher_id}")
print(f"   Student: {student_id}")
print(f"   Period: {period}")

# Prepare form data
form_data = {
    'class_id': class_id,
    'teacher_id': teacher_id,
    f'attendance_{student_id}_{period}': 'on',  # checked = present
    f'remark_{student_id}_general': 'Good attendance test',
    f'notes_{student_id}_general': 'Test note'
}

# POST the data
response = requests.post(f"{BASE_URL}/attendance-tabs/save", data=form_data)
print(f"   Response status: {response.status_code}")
print(f"   Response: {response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]}")

# Check database for the saved record
print("\n3. Checking database for saved record...")
today = datetime.now().strftime('%Y-%m-%d')

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, student_id, period, status, remark, notes, class_id, teacher_id, date
    FROM attendance 
    WHERE student_id = %s AND class_id = %s AND date = %s AND period = %s
    ORDER BY id DESC
    LIMIT 1
""", (student_id, class_id, today, period))

result = cursor.fetchone()

if result:
    print("   ✅ Record FOUND in database!")
    print(f"   ID: {result[0]}")
    print(f"   Student: {result[1]}")
    print(f"   Period: {result[2]}")
    print(f"   Status: {result[3]}")
    print(f"   Remark: {result[4]}")
    print(f"   Notes: {result[5]}")
    print(f"   Class: {result[6]}")
    print(f"   Teacher: {result[7]}")
    print(f"   Date: {result[8]}")
else:
    print("   ❌ NO RECORD FOUND in database!")
    print("   Checking if there are any attendance records for today...")
    
    cursor.execute("""
        SELECT COUNT(*) FROM attendance WHERE date = %s
    """, (today,))
    count_result = cursor.fetchone()
    print(f"   Total attendance records today: {count_result[0]}")

conn.close()

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
