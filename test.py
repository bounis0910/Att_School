#!/usr/bin/env python3
"""
Test script to check attendance table and fix sequence issues
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
db_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'adminit',
    'password': 'Bel@1981',
    'database': 'attdbsch'
}

def main():
    conn = psycopg2.connect(**db_params)
    conn.autocommit = False
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 80)
    print("ATTENDANCE TABLE DIAGNOSTICS")
    print("=" * 80)
    
    # 1. Check table structure
    print("\n1. TABLE STRUCTURE:")
    cursor.execute("""
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'attendance'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"   {col['column_name']:15} {col['data_type']:15} Default: {col['column_default'] or 'None':30} Nullable: {col['is_nullable']}")
    
    # 2. Check current max ID
    print("\n2. CURRENT DATA:")
    cursor.execute("SELECT COUNT(*) as count, MAX(id) as max_id FROM attendance")
    result = cursor.fetchone()
    print(f"   Total records: {result['count']}")
    print(f"   Max ID: {result['max_id']}")
    
    # 3. Check sequence (if exists)
    print("\n3. SEQUENCE CHECK:")
    cursor.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_name LIKE '%attendance%'
    """)
    sequences = cursor.fetchall()
    if sequences:
        for seq in sequences:
            print(f"   Sequence: {seq['sequence_name']}")
            # Get last value directly
            cursor.execute(f"SELECT last_value FROM {seq['sequence_name']}")
            val = cursor.fetchone()
            print(f"   Last value: {val['last_value']}")
    else:
        print("   No sequence found for attendance table!")
    
    # 4. Check primary key and constraints
    print("\n4. CONSTRAINTS:")
    cursor.execute("""
        SELECT conname, contype, pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conrelid = 'attendance'::regclass
    """)
    constraints = cursor.fetchall()
    for const in constraints:
        print(f"   {const['conname']:30} Type: {const['contype']} - {const['definition']}")
    
    # 5. Try to find the issue
    print("\n5. DIAGNOSIS:")
    
    # Check if id column has a default
    cursor.execute("""
        SELECT column_default
        FROM information_schema.columns
        WHERE table_name = 'attendance' AND column_name = 'id'
    """)
    id_default = cursor.fetchone()
    
    if not id_default or not id_default['column_default']:
        print("   ⚠️  WARNING: 'id' column has no default value!")
        print("   This means it's not auto-incrementing!")
    else:
        print(f"   ✓ ID column default: {id_default['column_default']}")
    
    # 6. Try to get sequence info directly
    cursor.execute("""
        SELECT pg_get_serial_sequence('attendance', 'id') as sequence_name
    """)
    seq_name_result = cursor.fetchone()
    sequence_name = seq_name_result['sequence_name'] if seq_name_result else None
    
    if sequence_name:
        print(f"\n6. SEQUENCE DETAILS for {sequence_name}:")
        cursor.execute(f"SELECT last_value, is_called FROM {sequence_name}")
        seq_info = cursor.fetchone()
        print(f"   Last value: {seq_info['last_value']}")
        print(f"   Is called: {seq_info['is_called']}")
        
        # Check if sequence is out of sync
        if result['max_id'] and seq_info['last_value'] <= result['max_id']:
            print(f"\n   ⚠️  PROBLEM FOUND: Sequence ({seq_info['last_value']}) <= Max ID ({result['max_id']})")
            print(f"   This will cause duplicate key errors!")
            
            # Fix the sequence
            new_value = result['max_id'] + 1
            print(f"\n7. FIXING SEQUENCE:")
            print(f"   Setting sequence to {new_value}...")
            cursor.execute(f"SELECT setval('{sequence_name}', %s, false)", (new_value,))
            conn.commit()
            print(f"   ✓ Sequence fixed!")
            
            # Verify
            cursor.execute(f"SELECT last_value FROM {sequence_name}")
            new_val = cursor.fetchone()
            print(f"   New sequence value: {new_val['last_value']}")
    else:
        print("\n6. NO SEQUENCE FOUND!")
        print("   The attendance table may not have a proper auto-increment setup.")
        print("   Checking if we need to create one...")
        
        # Check if id is integer type
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'attendance' AND column_name = 'id'
        """)
        id_type = cursor.fetchone()
        print(f"   ID column type: {id_type['data_type']}")
        
        if id_type['data_type'] == 'integer':
            print("\n7. CREATING SEQUENCE:")
            try:
                # Create sequence
                cursor.execute("CREATE SEQUENCE IF NOT EXISTS attendance_id_seq")
                # Set it to correct value
                max_id = result['max_id'] or 0
                cursor.execute("SELECT setval('attendance_id_seq', %s, true)", (max_id,))
                # Set as default for id column
                cursor.execute("ALTER TABLE attendance ALTER COLUMN id SET DEFAULT nextval('attendance_id_seq')")
                # Set sequence ownership
                cursor.execute("ALTER SEQUENCE attendance_id_seq OWNED BY attendance.id")
                conn.commit()
                print("   ✓ Sequence created and configured!")
            except Exception as e:
                print(f"   ✗ Error creating sequence: {e}")
                conn.rollback()
    
    print("\n" + "=" * 80)
    conn.close()

if __name__ == '__main__':
    main()
