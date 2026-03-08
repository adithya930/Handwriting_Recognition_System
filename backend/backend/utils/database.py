"""
Database Module
Handles MySQL database operations for storing recognition results
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import logging

# Setup logger
logger = logging.getLogger(__name__)


class Database:
    """
    MySQL database handler for handwriting recognition system
    """
    
    def __init__(self, host, user, password, database):
        """
        Initialize database connection
        
        Args:
            host (str): Database host
            user (str): Database user
            password (str): Database password
            database (str): Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def ensure_connection(self) -> bool:
        """
        Ensure there is an active MySQL connection; attempt reconnect if needed.
        Returns True if connected, else False.
        """
        try:
            if self.connection and self.connection.is_connected():
                return True
        except Exception:
            # fall through to reconnect
            pass
        return self.connect()
    
    def connect(self):
        """
        Establish database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                logger.info(f"Connected to MySQL database: {self.database}")
                return True
        
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """
        Close database connection
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def create_tables(self):
        """
        Create necessary database tables if they don't exist
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Create users table
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

            # Create recognition_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recognition_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    image_path VARCHAR(500) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    recognized_text TEXT,
                    confidence_score FLOAT,
                    processing_time FLOAT,
                    num_characters INT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_confidence (confidence_score),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Create user_uploads table (for tracking uploads)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_uploads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INT,
                    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
                    INDEX idx_status (status),
                    INDEX idx_upload_timestamp (upload_timestamp),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Check for missing user_id columns in existing tables
            try:
                cursor.execute("SHOW COLUMNS FROM recognition_results LIKE 'user_id'")
                if not cursor.fetchone():
                    logger.info("Adding user_id column to recognition_results")
                    cursor.execute("ALTER TABLE recognition_results ADD COLUMN user_id INT AFTER id")
                    cursor.execute("CREATE INDEX idx_user_id ON recognition_results(user_id)")
                
                cursor.execute("SHOW COLUMNS FROM user_uploads LIKE 'user_id'")
                if not cursor.fetchone():
                    logger.info("Adding user_id column to user_uploads")
                    cursor.execute("ALTER TABLE user_uploads ADD COLUMN user_id INT AFTER id")
                    cursor.execute("CREATE INDEX idx_user_id ON user_uploads(user_id)")
            except Error as e:
                logger.warning(f"Note: Could not alter tables to add user_id: {e}")
            
            self.connection.commit()
            cursor.close()
            print("Database tables created successfully")
            return True
        
        except Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_recognition_result(self, image_path=None, original_filename=None, 
                                  recognized_text=None, confidence_score=0.0, 
                                  processing_time=0.0, num_characters=0, metadata=None,
                                  upload_id=None, confidence=None, method=None, user_id=None):
        """
        Insert a recognition result into database
        
        Args:
            image_path (str): Path to processed image
            original_filename (str): Original filename
            recognized_text (str): Recognized text
            confidence_score (float): Overall confidence score (legacy)
            confidence (float): Confidence score (new param, same as confidence_score)
            processing_time (float): Processing time in seconds
            num_characters (int): Number of characters recognized
            metadata (dict, optional): Additional metadata
            upload_id (int, optional): Associated upload record ID
            method (str, optional): Recognition method used
            user_id (int, optional): User ID for foreign key
            
        Returns:
            int: Inserted record ID, or None if failed
        """
        try:
            if not self.ensure_connection():
                logger.error("MySQL Connection not available.")
                return None
            cursor = self.connection.cursor()
            
            # Handle parameter aliases
            if confidence is not None:
                confidence_score = confidence
            
            # Add method to metadata if provided
            if method and metadata is None:
                metadata = {'method': method}
            elif method and isinstance(metadata, dict):
                metadata['method'] = method
            
            # Cast numpy types to native Python types to avoid MySQL conversion errors
            confidence_score = float(confidence_score) if confidence_score else 0.0
            processing_time = float(processing_time) if processing_time else 0.0
            num_characters = int(num_characters) if num_characters else 0
            metadata_json = json.dumps(metadata) if metadata else None

            # Build query with or without user_id
            if user_id:
                query = """
                    INSERT INTO recognition_results 
                    (image_path, original_filename, recognized_text, confidence_score, 
                     processing_time, num_characters, metadata, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    str(image_path) if image_path else '',
                    str(original_filename) if original_filename else '',
                    str(recognized_text) if recognized_text is not None else '',
                    confidence_score,
                    processing_time,
                    num_characters,
                    metadata_json,
                    user_id
                )
            else:
                query = """
                    INSERT INTO recognition_results 
                    (image_path, original_filename, recognized_text, confidence_score, 
                     processing_time, num_characters, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    str(image_path) if image_path else '',
                    str(original_filename) if original_filename else '',
                    str(recognized_text) if recognized_text is not None else '',
                    confidence_score,
                    processing_time,
                    num_characters,
                    metadata_json
                )
            
            cursor.execute(query, values)
            self.connection.commit()
            
            record_id = cursor.lastrowid
            cursor.close()
            
            logger.info(f"Recognition result inserted with ID: {record_id}")
            return record_id
        
        except Error as e:
            logger.error(f"Error inserting recognition result: {e}")
            return None
    
    def insert_upload(self, filename, file_path, file_size, status='pending', user_id=None):
        """
        Insert upload record
        
        Args:
            filename (str): Original filename
            file_path (str): Stored file path
            file_size (int): File size in bytes
            status (str): Upload status
            user_id (int): User ID (optional)
            
        Returns:
            int: Inserted record ID, or None if failed
        """
        try:
            if not self.ensure_connection():
                logger.error("MySQL Connection not available.")
                return None
            cursor = self.connection.cursor()
            
            # Check if user_id column exists and include it if provided
            if user_id:
                query = """
                    INSERT INTO user_uploads 
                    (filename, file_path, file_size, status, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (filename, file_path, file_size, status, user_id)
            else:
                query = """
                    INSERT INTO user_uploads 
                    (filename, file_path, file_size, status)
                    VALUES (%s, %s, %s, %s)
                """
                values = (filename, file_path, file_size, status)
            
            cursor.execute(query, values)
            self.connection.commit()
            
            record_id = cursor.lastrowid
            cursor.close()
            
            return record_id
        
        except Error as e:
            logger.error(f"Error inserting upload: {e}")
            return None
    
    def update_upload_status(self, upload_id, status):
        """
        Update upload status
        
        Args:
            upload_id (int): Upload record ID
            status (str): New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            query = "UPDATE user_uploads SET status = %s WHERE id = %s"
            cursor.execute(query, (status, upload_id))
            self.connection.commit()
            
            cursor.close()
            return True
        
        except Error as e:
            print(f"Error updating upload status: {e}")
            return False
    
    def get_recognition_history(self, limit=50, offset=0):
        """
        Retrieve recognition history
        
        Args:
            limit (int): Number of records to retrieve
            offset (int): Offset for pagination
            
        Returns:
            List[dict]: List of recognition records
        """
        def _run_once():
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM recognition_results 
                ORDER BY timestamp DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            results_local = cursor.fetchall()
            cursor.close()
            return results_local

        try:
            if not self.ensure_connection():
                print("MySQL Connection not available.")
                return []
            results = _run_once()
        except Error as e:
            # Retry once on lost connection
            if getattr(e, 'errno', None) in (2006, 2013):
                print("Connection lost during history query. Reconnecting and retrying once...")
                if self.connect():
                    try:
                        results = _run_once()
                    except Error as e2:
                        print(f"Error retrieving history after retry: {e2}")
                        return []
                else:
                    return []
            else:
                print(f"Error retrieving history: {e}")
                return []

        # Convert JSON strings back to dict
        for result in results:
            if result['metadata']:
                result['metadata'] = json.loads(result['metadata'])

        return results
    
    def get_recognition_by_id(self, record_id):
        """
        Get specific recognition result by ID
        
        Args:
            record_id (int): Record ID
            
        Returns:
            dict: Recognition record or None
        """
        def _run_once():
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM recognition_results WHERE id = %s"
            cursor.execute(query, (record_id,))
            row = cursor.fetchone()
            cursor.close()
            return row

        try:
            if not self.ensure_connection():
                print("MySQL Connection not available.")
                return None
            result = _run_once()
        except Error as e:
            if getattr(e, 'errno', None) in (2006, 2013):
                print("Connection lost during record query. Reconnecting and retrying once...")
                if self.connect():
                    try:
                        result = _run_once()
                    except Error as e2:
                        print(f"Error retrieving record after retry: {e2}")
                        return None
                else:
                    return None
            else:
                print(f"Error retrieving record: {e}")
                return None

        if result and result.get('metadata'):
            result['metadata'] = json.loads(result['metadata'])
        return result
    
    def search_by_text(self, search_term, limit=50):
        """
        Search recognition results by text content
        
        Args:
            search_term (str): Text to search for
            limit (int): Maximum results to return
            
        Returns:
            List[dict]: Matching recognition records
        """
        def _run_once():
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM recognition_results 
                WHERE recognized_text LIKE %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, limit))
            rows = cursor.fetchall()
            cursor.close()
            return rows

        try:
            if not self.ensure_connection():
                print("MySQL Connection not available.")
                return []
            results = _run_once()
        except Error as e:
            if getattr(e, 'errno', None) in (2006, 2013):
                print("Connection lost during search. Reconnecting and retrying once...")
                if self.connect():
                    try:
                        results = _run_once()
                    except Error as e2:
                        print(f"Error searching after retry: {e2}")
                        return []
                else:
                    return []
            else:
                print(f"Error searching: {e}")
                return []

        for result in results:
            if result['metadata']:
                result['metadata'] = json.loads(result['metadata'])
        return results
    
    def get_statistics(self):
        """
        Get database statistics
        
        Returns:
            dict: Statistics about stored data
        """
        def _run_once():
            local = {}
            
            # Use separate cursor for each query to avoid "commands out of sync" error
            # Get total scans
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM recognition_results")
            result = cursor.fetchone()
            local['total_scans'] = int(result['total']) if result and result['total'] is not None else 0
            cursor.close()
            logger.debug(f"Total scans: {local['total_scans']}")
            
            # Get average confidence
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT AVG(confidence_score) as avg_confidence FROM recognition_results")
            result = cursor.fetchone()
            avg_conf = result['avg_confidence'] if result else None
            local['average_confidence'] = float(avg_conf) if avg_conf is not None else 0.0
            cursor.close()
            logger.debug(f"Average confidence: {local['average_confidence']}")
            
            # Get total characters
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT SUM(num_characters) as total_chars FROM recognition_results")
            result = cursor.fetchone()
            total_chars = result['total_chars'] if result else None
            local['total_characters'] = int(total_chars) if total_chars is not None else 0
            cursor.close()
            
            # Get average processing time
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT AVG(processing_time) as avg_time FROM recognition_results")
            result = cursor.fetchone()
            avg_time = result['avg_time'] if result else None
            local['average_processing_time'] = float(avg_time) if avg_time is not None else 0.0
            cursor.close()
            
            # Calculate success rate (assume all completed records are successful if confidence > 0.5)
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as successful FROM recognition_results WHERE confidence_score > 0.5")
            result = cursor.fetchone()
            successful = int(result['successful']) if result and result['successful'] is not None else 0
            cursor.close()
            local['success_rate'] = float((successful / local['total_scans'] * 100)) if local['total_scans'] > 0 else 0.0
            logger.debug(f"Success rate: {local['success_rate']}%")
            
            # Get today's scans
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as today FROM recognition_results WHERE DATE(timestamp) = CURDATE()")
            result = cursor.fetchone()
            local['today_scans'] = int(result['today']) if result and result['today'] is not None else 0
            cursor.close()
            logger.debug(f"Today's scans: {local['today_scans']}")
            
            # Recognition Trends (Last 7 Days)
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATE(timestamp) as scan_date, COUNT(*) as count 
                FROM recognition_results 
                WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
                GROUP BY DATE(timestamp)
                ORDER BY scan_date
            """)
            trends = cursor.fetchall()
            local['trends'] = {str(item['scan_date']): int(item['count']) for item in trends}
            cursor.close()
            logger.debug(f"Trends data: {local['trends']}")
            
            # Confidence Distribution
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN confidence_score < 0.2 THEN 1 ELSE 0 END) as '0-20%',
                    SUM(CASE WHEN confidence_score >= 0.2 AND confidence_score < 0.4 THEN 1 ELSE 0 END) as '20-40%',
                    SUM(CASE WHEN confidence_score >= 0.4 AND confidence_score < 0.6 THEN 1 ELSE 0 END) as '40-60%',
                    SUM(CASE WHEN confidence_score >= 0.6 AND confidence_score < 0.8 THEN 1 ELSE 0 END) as '60-80%',
                    SUM(CASE WHEN confidence_score >= 0.8 THEN 1 ELSE 0 END) as '80-100%'
                FROM recognition_results
            """)
            dist = cursor.fetchone()
            # Ensure we return 0 instead of None, and cast to int to avoid Decimal issues
            local['confidence_distribution'] = {k: int(v) if v is not None else 0 for k, v in dist.items()}
            cursor.close()
            logger.debug(f"Confidence distribution: {local['confidence_distribution']}")
            
            logger.info("Statistics retrieved successfully")
            return local

        try:
            if not self.ensure_connection():
                logger.error("MySQL Connection not available for statistics query")
                return {
                    'total_scans': 0,
                    'average_confidence': 0.0,
                    'total_characters': 0,
                    'average_processing_time': 0.0,
                    'success_rate': 0.0,
                    'today_scans': 0,
                    'trends': {},
                    'confidence_distribution': {}
                }
            stats = _run_once()
        except Error as e:
            if getattr(e, 'errno', None) in (2006, 2013):
                logger.warning("Connection lost during statistics query. Reconnecting and retrying once...")
                if self.connect():
                    try:
                        stats = _run_once()
                    except Error as e2:
                        logger.error(f"Error getting statistics after retry: {e2}")
                        return {
                            'total_scans': 0,
                            'average_confidence': 0.0,
                            'total_characters': 0,
                            'average_processing_time': 0.0,
                            'success_rate': 0.0,
                            'today_scans': 0,
                            'trends': {},
                            'confidence_distribution': {}
                        }
                else:
                    logger.error("Failed to reconnect for statistics query")
                    return {
                        'total_scans': 0,
                        'average_confidence': 0.0,
                        'total_characters': 0,
                        'average_processing_time': 0.0,
                        'success_rate': 0.0,
                        'today_scans': 0,
                        'trends': {},
                        'confidence_distribution': {}
                    }
            else:
                logger.error(f"Error getting statistics: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return {
                    'total_scans': 0,
                    'average_confidence': 0.0,
                    'total_characters': 0,
                    'average_processing_time': 0.0,
                    'success_rate': 0.0,
                    'today_scans': 0,
                    'trends': {},
                    'confidence_distribution': {}
                }

        return stats
    
    def delete_old_records(self, days=30):
        """
        Delete records older than specified days
        
        Args:
            days (int): Number of days to keep
            
        Returns:
            int: Number of deleted records
        """
        try:
            cursor = self.connection.cursor()
            
            query = """
                DELETE FROM recognition_results 
                WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            cursor.execute(query, (days,))
            self.connection.commit()
            
            deleted_count = cursor.rowcount
            cursor.close()
            
            print(f"Deleted {deleted_count} old records")
            return deleted_count
        
        except Error as e:
            print(f"Error deleting old records: {e}")
            return 0

    # ==================== User Authentication Methods ====================
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = None, role: str = 'staff') -> int:
        """
        Create a new user account
        
        Args:
            username (str): Unique username
            email (str): User email
            password_hash (str): Hashed password
            full_name (str): Full name (optional)
            role (str): User role (default: 'staff')
            
        Returns:
            int: User ID if successful, None otherwise
        """
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (username, email, password_hash, full_name, role))
            self.connection.commit()
            
            user_id = cursor.lastrowid
            cursor.close()
            
            print(f"User created with ID: {user_id}")
            return user_id
            
        except Error as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> dict:
        """
        Get user by username
        
        Args:
            username (str): Username to search for
            
        Returns:
            dict: User data or None if not found
        """
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, username, email, password_hash, full_name, role, 
                       is_active, created_at, last_login
                FROM users
                WHERE username = %s
            """
            
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            
            return user
            
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> dict:
        """
        Get user by email
        
        Args:
            email (str): Email to search for
            
        Returns:
            dict: User data or None if not found
        """
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, username, email, password_hash, full_name, role, 
                       is_active, created_at, last_login
                FROM users
                WHERE email = %s
            """
            
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            
            return user
            
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if successful
        """
        if not self.ensure_connection():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                UPDATE users
                SET last_login = NOW()
                WHERE id = %s
            """
            
            cursor.execute(query, (user_id,))
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"Error updating last login: {e}")
            return False
    
    def get_user_by_id(self, user_id: int) -> dict:
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User data or None if not found
        """
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, username, email, full_name, role, 
                       is_active, created_at, last_login
                FROM users
                WHERE id = %s
            """
            
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            return user
            
        except Error as e:
            print(f"Error fetching user: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    db = Database(
        host='localhost',
        user='root',
        password='your_password',
        database='handwriting_db'
    )
    
    if db.connect():
        db.create_tables()
        
        # Test insert
        record_id = db.insert_recognition_result(
            image_path='/path/to/image.jpg',
            original_filename='test.jpg',
            recognized_text='Hello World',
            confidence_score=0.95,
            processing_time=2.3,
            num_characters=11,
            metadata={'model_version': '1.0'}
        )
        
        # Get statistics
        stats = db.get_statistics()
        print("Statistics:", stats)
        
        db.disconnect()
