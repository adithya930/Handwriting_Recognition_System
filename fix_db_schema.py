import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

def migrate():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'medical_prescription_db')
        )
        cursor = conn.cursor()
        
        tables_to_fix = ['recognition_results', 'user_uploads']
        
        for table in tables_to_fix:
            print(f"Checking table: {table}")
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'user_id'")
            if not cursor.fetchone():
                print(f"Adding user_id to {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INT AFTER id")
                cursor.execute(f"CREATE INDEX idx_user_id ON {table}(user_id)")
                print(f"Column user_id added to {table}")
            else:
                print(f"user_id already exists in {table}")
        
        # Ensure users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    role ENUM('doctor', 'pharmacist', 'admin', 'staff') DEFAULT 'staff',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("Users table created.")
        
        conn.commit()
        conn.close()
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
