-- MySQL Database Schema for Medical Prescription Recognition System
-- Create database and tables

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS medical_prescription_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE medical_prescription_db;

-- Table for users (authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Unique username',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'User email address',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password',
    full_name VARCHAR(100) COMMENT 'User full name',
    role ENUM('doctor', 'pharmacist', 'admin', 'staff') DEFAULT 'staff' COMMENT 'User role',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Account active status',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation time',
    last_login DATETIME COMMENT 'Last login timestamp',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User accounts for medical prescription system';

-- Table for storing recognition results
CREATE TABLE IF NOT EXISTS recognition_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User who processed this prescription',
    image_path VARCHAR(500) NOT NULL COMMENT 'Path to processed image',
    original_filename VARCHAR(255) NOT NULL COMMENT 'Original uploaded filename',
    recognized_text TEXT COMMENT 'Final recognized prescription text',
    confidence_score FLOAT COMMENT 'Average confidence score (0-1)',
    processing_time FLOAT COMMENT 'Processing time in seconds',
    num_characters INT COMMENT 'Number of characters recognized',
    prescription_type VARCHAR(50) COMMENT 'Type of prescription (handwritten/printed)',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Recognition timestamp',
    metadata JSON COMMENT 'Additional metadata (preprocessing details, medications, etc.)',
    
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_confidence (confidence_score),
    INDEX idx_filename (original_filename),
    FULLTEXT INDEX idx_text (recognized_text),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores medical prescription recognition results';

-- Table for tracking user uploads
CREATE TABLE IF NOT EXISTS user_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User who uploaded the file',
    filename VARCHAR(255) NOT NULL COMMENT 'Original filename',
    file_path VARCHAR(500) NOT NULL COMMENT 'Stored file path',
    file_size INT COMMENT 'File size in bytes',
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Upload time',
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT 'Processing status',
    error_message TEXT COMMENT 'Error message if processing failed',
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_upload_timestamp (upload_timestamp),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tracks uploaded prescription files and their processing status';

-- Table for system statistics (optional)
CREATE TABLE IF NOT EXISTS system_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE COMMENT 'Date of statistics',
    total_recognitions INT DEFAULT 0 COMMENT 'Total recognitions for the day',
    total_characters INT DEFAULT 0 COMMENT 'Total characters processed',
    avg_confidence FLOAT COMMENT 'Average confidence score',
    avg_processing_time FLOAT COMMENT 'Average processing time',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Daily system statistics';

-- Table for user feedback (optional - for future enhancement)
CREATE TABLE IF NOT EXISTS user_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recognition_id INT NOT NULL COMMENT 'Related recognition result ID',
    corrected_text TEXT COMMENT 'User-corrected text',
    rating INT COMMENT 'User rating (1-5)',
    comments TEXT COMMENT 'User comments',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (recognition_id) REFERENCES recognition_results(id) ON DELETE CASCADE,
    INDEX idx_recognition_id (recognition_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='User feedback for recognition results';

-- Create a view for recent recognitions
CREATE OR REPLACE VIEW recent_recognitions AS
SELECT 
    r.id,
    r.original_filename,
    r.recognized_text,
    r.confidence_score,
    r.num_characters,
    r.processing_time,
    r.timestamp,
    u.status AS upload_status
FROM recognition_results r
LEFT JOIN user_uploads u ON r.original_filename = u.filename
ORDER BY r.timestamp DESC
LIMIT 100;

-- Create a view for statistics summary
CREATE OR REPLACE VIEW statistics_summary AS
SELECT 
    COUNT(*) as total_recognitions,
    SUM(num_characters) as total_characters,
    AVG(confidence_score) as avg_confidence,
    AVG(processing_time) as avg_processing_time,
    MIN(timestamp) as first_recognition,
    MAX(timestamp) as last_recognition
FROM recognition_results;

-- Stored procedure to clean old records
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS clean_old_records(IN days_to_keep INT)
BEGIN
    DECLARE deleted_count INT;
    
    -- Delete old recognition results
    DELETE FROM recognition_results
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);
    
    SET deleted_count = ROW_COUNT();
    
    -- Delete old uploads
    DELETE FROM user_uploads
    WHERE upload_timestamp < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);
    
    SELECT CONCAT('Deleted ', deleted_count, ' old records') AS result;
END //

DELIMITER ;

-- Stored procedure to update daily statistics
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS update_daily_stats()
BEGIN
    INSERT INTO system_stats (
        stat_date,
        total_recognitions,
        total_characters,
        avg_confidence,
        avg_processing_time
    )
    SELECT 
        CURDATE() as stat_date,
        COUNT(*) as total_recognitions,
        SUM(num_characters) as total_characters,
        AVG(confidence_score) as avg_confidence,
        AVG(processing_time) as avg_processing_time
    FROM recognition_results
    WHERE DATE(timestamp) = CURDATE()
    ON DUPLICATE KEY UPDATE
        total_recognitions = VALUES(total_recognitions),
        total_characters = VALUES(total_characters),
        avg_confidence = VALUES(avg_confidence),
        avg_processing_time = VALUES(avg_processing_time);
END //

DELIMITER ;

-- Insert sample configuration data (optional)
-- You can use this to store application configuration in database

CREATE TABLE IF NOT EXISTS app_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Application configuration settings';

-- Insert default configurations
INSERT INTO app_config (config_key, config_value, description) VALUES
('model_version', '1.0', 'Current model version'),
('confidence_threshold', '0.5', 'Minimum confidence threshold'),
('enable_spell_check', 'true', 'Enable spell checking'),
('max_file_size_mb', '16', 'Maximum upload file size in MB')
ON DUPLICATE KEY UPDATE config_value=VALUES(config_value);

-- Grant permissions (adjust as needed for your setup)
-- CREATE USER IF NOT EXISTS 'handwriting_user'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON handwriting_db.* TO 'handwriting_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Show created tables
SHOW TABLES;

-- Display table structures
DESCRIBE recognition_results;
DESCRIBE user_uploads;
DESCRIBE system_stats;
DESCRIBE user_feedback;
DESCRIBE app_config;

SELECT 'Database schema created successfully!' AS Status;
