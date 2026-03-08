"""
Flask Backend Application
Provides REST API for Medical Prescription Recognition System
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import traceback
import logging
from datetime import datetime

# Import custom modules
from config import *
from utils.database import Database
from utils.deepseek_vision import DeepSeekVision
from utils.auth import AuthManager, token_required, role_required, login_required

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enable CORS
CORS(app, origins=CORS_ORIGINS)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize DeepSeek AI Vision (AI-powered text recognition)
deepseek_vision = DeepSeekVision()

# Initialize database
db = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

# Initialize authentication manager
auth_manager = AuthManager(SECRET_KEY)


def initialize_database():
    """
    Initialize database connection and tables
    """
    try:
        if db.connect():
            db.create_tables()
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Failed to connect to database")
            return False
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False


def allowed_file(filename):
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Filename to check
        
    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Serve the landing page
    """
    # Check if user is logged in
    if 'user_id' in session:
        return render_template('home.html')
    return render_template('index.html')


@app.route('/login')
def login_page():
    """
    Serve the login page
    """
    # Redirect to home if already logged in
    if 'user_id' in session:
        return render_template('home.html')
    return render_template('login.html')


@app.route('/register')
def register_page():
    """
    Serve the registration page
    """
    # Redirect to home if already logged in
    if 'user_id' in session:
        return render_template('home.html')
    return render_template('register.html')


@app.route('/api/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    Expected JSON:
        {
            "username": "user123",
            "email": "user@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "role": "staff"  # optional, defaults to 'staff'
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data.get('full_name', '').strip()
        role = data.get('role', 'staff')
        
        # Ensure full_name is not empty
        if not full_name:
            full_name = username
        
        # Validate username
        is_valid, error_msg = auth_manager.validate_username(username)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Validate email
        if not auth_manager.validate_email(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error_msg = auth_manager.validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Check if username already exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username already taken'
            }), 409
        
        # Check if email already exists
        existing_email = db.get_user_by_email(email)
        if existing_email:
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
        
        # Hash password
        password_hash = auth_manager.hash_password(password)
        
        # Create user
        user_id = db.create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role
        )
        
        if user_id:
            logger.info(f"New user registered: {username} (ID: {user_id})")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'user_id': user_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create user account'
            }), 500
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(f"Registration error details: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Expected JSON:
        {
            "username": "user123",  # or email
            "password": "password123"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        username_or_email = data['username'].strip()
        password = data['password']
        
        # Try to find user by username or email
        user = db.get_user_by_username(username_or_email)
        if not user:
            user = db.get_user_by_email(username_or_email)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({
                'success': False,
                'error': 'Account is disabled'
            }), 403
        
        # Verify password
        if not auth_manager.verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Generate token
        token = auth_manager.generate_token(
            user_id=user['id'],
            username=user['username'],
            role=user['role']
        )
        
        # Store in session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['token'] = token
        
        logger.info(f"User logged in: {user['username']}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """
    User logout endpoint
    """
    try:
        username = session.get('username', 'Unknown')
        
        # Clear session
        session.clear()
        
        logger.info(f"User logged out: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500


@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current logged-in user information
    """
    try:
        user_id = session.get('user_id')
        user = db.get_user_by_id(user_id)
        
        if user:
            # Convert datetime to string
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
            if user.get('last_login'):
                user['last_login'] = user['last_login'].isoformat()
            
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user information'
        }), 500


@app.route('/home')
def home():
    """
    Serve the dashboard/home page (protected)
    """
    if 'user_id' not in session:
        return render_template('index.html')
    return render_template('home.html')


@app.route('/camera')
def camera_page():
    """
    Serve the camera capture page
    """
    return render_template('camera.html')


@app.route('/upload')
def upload_page():
    """
    Serve the upload page
    """
    return render_template('upload.html')


@app.route('/history')
def history_page():
    """
    Serve the history page
    """
    return render_template('history.html')


@app.route('/test-stats')
def test_stats_page():
    """
    Serve the statistics test page
    """
    return render_template('test_stats.html')


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """
    Serve uploaded images
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db.connection is not None and db.connection.is_connected(),
        'deepseek_ai_available': deepseek_vision.available
    })


@app.route('/api/recognize', methods=['POST'])
def recognize_text():
    """
    Main endpoint for prescription text recognition
    
    Accepts: multipart/form-data with 'image' file
    Returns: JSON with recognized text and metadata
    """
    start_time = time.time()
    
    try:
        # Check if DeepSeek AI is available
        if not deepseek_vision.available:
            return jsonify({
                'success': False,
                'error': 'DeepSeek AI not available. Please check API key configuration.'
            }), 500
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        logger.info(f"Processing file: {unique_filename}")
        
        # Get user_id from session (for foreign key constraint)
        user_id = session.get('user_id')
        logger.info(f"User ID from session: {user_id}")
        
        # Record upload in database
        file_size = os.path.getsize(upload_path)
        logger.info(f"Inserting upload record: filename={filename}, size={file_size}, user_id={user_id}")
        upload_id = db.insert_upload(filename, upload_path, file_size, status='processing', user_id=user_id)
        logger.info(f"Upload record inserted with ID: {upload_id}")
        
        # Use DeepSeek AI Vision for text recognition
        logger.info("Using DeepSeek AI Vision for text recognition")
        deepseek_result = deepseek_vision.recognize_text_from_path(upload_path, detailed=True)
        
        if deepseek_result['success']:
            logger.info(f"DeepSeek AI successful: confidence {deepseek_result['confidence']:.3f}")
            
            processing_time = time.time() - start_time
            logger.info(f"Inserting recognition result for upload_id={upload_id}, user_id={user_id}")
            result_id = db.insert_recognition_result(
                upload_id=upload_id,
                image_path=upload_path,
                original_filename=filename,
                recognized_text=deepseek_result['text'],
                confidence=deepseek_result['confidence'],
                processing_time=processing_time,
                num_characters=len(deepseek_result['text']),
                method='deepseek_ai',
                user_id=user_id,
                metadata={
                    'method': 'DeepSeek AI Vision',
                    'model': deepseek_result.get('model', 'deepseek-chat'),
                    'word_count': deepseek_result.get('word_count', 0),
                    'usage': deepseek_result.get('usage', {})
                }
            )
            logger.info(f"Recognition result inserted with ID: {result_id}")
            
            if upload_id:
                db.update_upload_status(upload_id, 'completed')
                logger.info(f"Upload status updated to 'completed' for ID: {upload_id}")
            
            return jsonify({
                'success': True,
                'text': deepseek_result['text'],
                'confidence': deepseek_result['confidence'],
                'method': 'DeepSeek AI Vision',
                'word_count': deepseek_result.get('word_count', 0),
                'processing_time': processing_time,
                'result_id': result_id,
                'upload_id': upload_id
            })
        else:
            # DeepSeek AI failed
            logger.error(f"DeepSeek AI recognition failed: {deepseek_result.get('error', 'Unknown error')}")
            
            if upload_id:
                db.update_upload_status(upload_id, 'failed')
            
            return jsonify({
                'success': False,
                'error': deepseek_result.get('error', 'Text recognition failed'),
                'processing_time': time.time() - start_time
            }), 500
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'processing_time': time.time() - start_time
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get recognition history
    
    Query params:
        limit (int): Number of records to return (default: 50)
        offset (int): Offset for pagination (default: 0)
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Validate parameters
        limit = min(max(1, limit), 100)  # Between 1 and 100
        offset = max(0, offset)
        
        history = db.get_recognition_history(limit=limit, offset=offset)
        
        # Convert datetime objects to strings
        for record in history:
            if 'timestamp' in record and record['timestamp']:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(history),
            'limit': limit,
            'offset': offset,
            'data': history
        })
    
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['GET'])
def search_text():
    """
    Search recognition results by text
    
    Query params:
        q (str): Search query
        limit (int): Max results (default: 50)
    """
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        results = db.search_by_text(query, limit=limit)
        
        # Convert datetime objects
        for record in results:
            if 'timestamp' in record and record['timestamp']:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Get system statistics
    """
    try:
        stats = db.get_statistics()
        logger.info(f"Returning statistics: {stats}")
        
        # Ensure stats has all required fields with default values
        default_stats = {
            'total_scans': 0,
            'average_confidence': 0.0,
            'total_characters': 0,
            'average_processing_time': 0.0,
            'success_rate': 0.0,
            'today_scans': 0,
            'trends': {},
            'confidence_distribution': {}
        }
        
        # Merge with actual stats (actual stats override defaults)
        final_stats = {**default_stats, **stats}
        
        return jsonify({
            'success': True,
            'statistics': final_stats
        })
    
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """
    Get specific recognition record
    """
    try:
        record = db.get_recognition_by_id(record_id)
        
        if record is None:
            return jsonify({
                'success': False,
                'error': 'Record not found'
            }), 404
        
        # Convert datetime
        if 'timestamp' in record and record['timestamp']:
            record['timestamp'] = record['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'record': record
        })
    
    except Exception as e:
        logger.error(f"Error fetching record: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def too_large(e):
    """
    Handle file too large error
    """
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_CONTENT_LENGTH / (1024*1024)}MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    """
    Handle 404 errors
    """
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """
    Handle 500 errors
    """
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Starting Handwriting Recognition System (DeepSeek AI)")
    logger.info("="*60)
    
    # Initialize database
    logger.info("Initializing database...")
    initialize_database()
    
    # Check DeepSeek AI availability
    if deepseek_vision.available:
        logger.info("DeepSeek AI Vision is ready")
    else:
        logger.warning("DeepSeek AI Vision is not available - check API key")
    
    logger.info(f"Server starting on {HOST}:{PORT}")
    logger.info("="*60)
    
    # Run Flask app
    app.run(host=HOST, port=PORT, debug=DEBUG)
