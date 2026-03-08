"""
Authentication Utilities
Handles user authentication, password hashing, and session management
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session
import os


class AuthManager:
    """
    Authentication manager for handling user authentication
    """
    
    def __init__(self, secret_key=None):
        """
        Initialize auth manager
        
        Args:
            secret_key (str): Secret key for JWT encoding
        """
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password (str): Plain text password
            hashed (str): Hashed password
            
        Returns:
            bool: True if password matches
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def generate_token(self, user_id: int, username: str, role: str, 
                      expires_hours: int = 24) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_id (int): User ID
            username (str): Username
            role (str): User role
            expires_hours (int): Token expiration time in hours
            
        Returns:
            str: JWT token
        """
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'exp': datetime.utcnow() + timedelta(hours=expires_hours),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            print(f"Error generating token: {e}")
            return None
    
    def decode_token(self, token: str) -> dict:
        """
        Decode and verify JWT token
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
    
    def validate_email(self, email: str) -> bool:
        """
        Basic email validation
        
        Args:
            email (str): Email address
            
        Returns:
            bool: True if valid format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Add more validation rules as needed
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        # has_digit = any(c.isdigit() for c in password)
        
        return True, None
    
    def validate_username(self, username: str) -> tuple:
        """
        Validate username format
        
        Args:
            username (str): Username to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username is too long"
        
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, None


def token_required(f):
    """
    Decorator to protect routes with token authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        # Get token from session
        elif 'token' in session:
            token = session['token']
        
        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        try:
            auth_manager = AuthManager()
            payload = auth_manager.decode_token(token)
            
            if not payload:
                return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
            
            # Add user info to request context
            request.current_user = payload
            
        except Exception as e:
            return jsonify({'success': False, 'error': 'Token verification failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user role
    
    Args:
        allowed_roles (list): List of allowed roles
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user_role = request.current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False, 
                    'error': 'Insufficient permissions'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def login_required(f):
    """
    Decorator to check if user is logged in (session-based)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Login required',
                'redirect': '/login'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated
