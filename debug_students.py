"""
Debug script to check student and class data
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:Almana@Pg23@localhost:5432/alsisdb')

def parse_db_url(url):
    """Parse DATABASE_URL for psycopg2 connection"""
    url = url.replace('+asyncpg', '').replace('+psycopg2', '')
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

db_params = parse_db_url(DATABASE_URL)

try:
    conn = psycopg2.connect(**db_params)
    conn.cursor_factory = RealDictCursor
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DEBUGGING: STUDENTS AND CLASSES")
    print("=" * 80)
    
    # Check all classes
    print("\n1. ALL CLASSES IN DATABASE:")
    print("-" * 80)
    cursor.execute("SELECT id, name FROM school_class ORDER BY id")
    classes = cursor.fetchall()
    if classes:
        for cls in classes:
            print(f"  Class ID: {cls['id']} (type: {type(cls['id'])}) - Name: {cls['name']}")
    else:
        print("  ❌ NO CLASSES FOUND")
    
    # Check all students
    print("\n2. ALL STUDENTS IN DATABASE:")
    print("-" * 80)
    cursor.execute("SELECT id, name, class_id FROM student ORDER BY id LIMIT 20")
    students = cursor.fetchall()
    if students:
        for std in students:
            class_id = std['class_id']
            print(f"  Student ID: {std['id']} - Name: {std['name']} - Class ID: {class_id} (type: {type(class_id).__name__})")
    else:
        print("  ❌ NO STUDENTS FOUND")
    
    # Count students per class
    print("\n3. STUDENT COUNT PER CLASS:")
    print("-" * 80)
    cursor.execute("""
        SELECT class_id, COUNT(*) as count 
        FROM student 
        GROUP BY class_id 
        ORDER BY class_id
    """)
    counts = cursor.fetchall()
    if counts:
        for row in counts:
            print(f"  Class ID: {row['class_id']} - Students: {row['count']}")
    else:
        print("  ❌ NO STUDENT COUNT DATA")
    
    # Check for NULL class_id
    print("\n4. STUDENTS WITH NULL CLASS_ID:")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM student WHERE class_id IS NULL")
    null_count = cursor.fetchone()
    if null_count['count'] > 0:
        print(f"  ⚠️  WARNING: {null_count['count']} students have NULL class_id")
        cursor.execute("SELECT id, name FROM student WHERE class_id IS NULL LIMIT 5")
        null_students = cursor.fetchall()
        for std in null_students:
            print(f"    - Student ID: {std['id']} - Name: {std['name']}")
    else:
        print("  ✓ All students have class_id assigned")
    
    # Test the query used in attendance_tabs
    print("\n5. TEST QUERY FOR ATTENDANCE_TABS:")
    print("-" * 80)
    cursor.execute("SELECT id FROM school_class LIMIT 1")
    first_class = cursor.fetchone()
    if first_class:
        class_id = first_class['id']
        print(f"  Testing with Class ID: {class_id}")
        cursor.execute("""
            SELECT * FROM student 
            WHERE class_id = %s 
            ORDER BY name
        """, (class_id,))
        test_students = cursor.fetchall()
        print(f"  Result: {len(test_students)} students found")
        if test_students:
            for std in test_students:
                print(f"    - {std['name']}")
    
    # Data type analysis
    print("\n6. DATA TYPE ANALYSIS:")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            column_name, 
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'school_class' 
        AND column_name = 'id'
    """)
    class_id_type = cursor.fetchone()
    if class_id_type:
        print(f"  school_class.id type: {class_id_type['data_type']} (nullable: {class_id_type['is_nullable']})")
    
    cursor.execute("""
        SELECT 
            column_name, 
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'student' 
        AND column_name = 'class_id'
    """)
    student_class_id_type = cursor.fetchone()
    if student_class_id_type:
        print(f"  student.class_id type: {student_class_id_type['data_type']} (nullable: {student_class_id_type['is_nullable']})")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
