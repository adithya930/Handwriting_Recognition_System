"""
Configuration settings for the application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Database settings
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')
DB_NAME = os.environ.get('DB_NAME', 'medical_prescription_db')

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'data', 'processed')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

# Model settings
MODEL_PATH = os.environ.get('MODEL_PATH', os.path.join(BASE_DIR, 'trained_models', 'model_standard_best.h5'))
if not os.path.isabs(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, MODEL_PATH)
MODEL_INPUT_SIZE = (28, 28)
NUM_CLASSES = 62

# Processing settings
CONFIDENCE_THRESHOLD = 0.5
ENABLE_SPELL_CHECK = True
PREPROCESSING_METHOD = 'bilateral'  # 'gaussian', 'median', 'bilateral'
BINARIZATION_METHOD = 'otsu'  # 'otsu', 'adaptive', 'simple'

# Server settings
HOST = '0.0.0.0'
PORT = 5000

# CORS settings
CORS_ORIGINS = '*'  # In production, specify allowed origins

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(BASE_DIR, 'app.log')

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'trained_models'), exist_ok=True)
