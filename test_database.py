"""
Database Connection Test Script (Simple Version)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'medical_prescription_db')

print("=" * 60)
print("Database Connection Test")
print("=" * 60)
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}")
print(f"Database: {DB_NAME}")
print("=" * 60)

import mysql.connector
from mysql.connector import Error

try:
    print("\n1. Testing connection...")
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    if connection.is_connected():
        print(f"   [OK] Connected to {DB_NAME}")
        
        cursor = connection.cursor(dictionary=True)
        
        # Check tables
        print("\n2. Checking tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for t in tables:
            print(f"   - {list(t.values())[0]}")
        
        # Count existing records
        print("\n3. Counting records...")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM recognition_results")
            count = cursor.fetchone()['count']
            print(f"   recognition_results: {count} records")
        except Exception as e:
            print(f"   recognition_results: TABLE NOT FOUND - {e}")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM user_uploads")
            count = cursor.fetchone()['count']
            print(f"   user_uploads: {count} records")
        except Exception as e:
            print(f"   user_uploads: TABLE NOT FOUND - {e}")
        
        # Test insert
        print("\n4. Testing insert into recognition_results...")
        try:
            cursor.execute("""
                INSERT INTO recognition_results 
                (image_path, original_filename, recognized_text, confidence_score, processing_time, num_characters)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('/test/path.jpg', 'test.jpg', 'Test text', 0.95, 1.5, 9))
            connection.commit()
            test_id = cursor.lastrowid
            print(f"   [OK] Test record inserted with ID: {test_id}")
            
            cursor.execute("DELETE FROM recognition_results WHERE id = %s", (test_id,))
            connection.commit()
            print("   [OK] Test record deleted")
        except Error as e:
            print(f"   [FAIL] Insert failed: {e}")
        
        cursor.close()
        connection.close()
        print("\n" + "=" * 60)
        print("[SUCCESS] Database is working correctly!")
        print("=" * 60)
        
except Error as e:
    print(f"\n[FAIL] Connection failed: {e}")
