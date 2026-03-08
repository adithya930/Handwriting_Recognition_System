# Authentication System - Setup & Usage Guide

## Overview
The authentication system has been successfully integrated into your Medical Prescription Recognition System. Users can now register, login, and access protected features.

## What Was Added

### 1. Backend Components

#### Authentication Module (`backend/utils/auth.py`)
- Password hashing with bcrypt
- JWT token generation and validation
- Email and password validation
- Decorators for protecting routes:
  - `@token_required` - Requires valid authentication token
  - `@role_required(['admin', 'doctor'])` - Requires specific user role
  - `@login_required` - Requires active session

#### New API Endpoints (`backend/app.py`)
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `POST /api/logout` - User logout
- `GET /api/me` - Get current user info

#### New Page Routes
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /` - Landing page (redirects to home if logged in)
- `GET /home` - Dashboard (requires authentication)

### 2. Frontend Components

#### Templates
- **login.html** - Login page with form validation
- **register.html** - Registration page with role selection
- Updated **index.html** - Landing page with login/register buttons
- Updated **home.html** - Added user info and logout button in sidebar

#### Stylesheets
- **auth.css** - Authentication pages styling
- Updated **sidebar.css** - Added user info section and logout button

#### JavaScript
- **auth.js** - Authentication logic, form handling, token management

### 3. Database
The users table already exists in your database with the following structure:
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('doctor', 'pharmacist', 'admin', 'staff') DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);
```

## How to Use

### 1. Start the Application
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python backend/app.py
```

### 2. Access the Application
Open your browser and navigate to: `http://localhost:5000`

### 3. User Registration
1. Click "Register" button on the landing page
2. Fill in the registration form:
   - Full Name
   - Username (3-50 characters, alphanumeric + underscores)
   - Email Address
   - Password (minimum 6 characters)
   - Confirm Password
   - Select Role (Staff, Doctor, Pharmacist)
3. Accept terms and conditions
4. Click "Create Account"
5. You'll be redirected to the login page

### 4. User Login
1. Click "Login" button or navigate to `/login`
2. Enter your username/email and password
3. Optionally check "Remember me" to save username
4. Click "Login"
5. You'll be redirected to the dashboard

### 5. Using the Application
Once logged in, you can:
- View dashboard with statistics
- Upload prescriptions via camera or file
- View recognition history
- Logout from the sidebar

## User Roles

The system supports 4 user roles:
- **Staff** (default) - Basic access
- **Doctor** - Can create and view prescriptions
- **Pharmacist** - Can process prescriptions
- **Admin** - Full system access

## Security Features

1. **Password Security**
   - Passwords are hashed using bcrypt
   - Minimum 6 characters required
   - Never stored in plain text

2. **Session Management**
   - JWT tokens for API authentication
   - Session-based authentication for web pages
   - Tokens expire after 24 hours

3. **Input Validation**
   - Email format validation
   - Username format validation
   - Password strength checking
   - XSS protection

## API Usage

### Register a New User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
    "role": "doctor"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

Response includes token:
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "doctor"
  }
}
```

### Access Protected Endpoint
```bash
curl http://localhost:5000/api/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout
```bash
curl -X POST http://localhost:5000/api/logout
```

## Protecting New Routes

To protect a new route, use the decorators:

```python
from utils.auth import login_required, token_required, role_required

# Session-based protection
@app.route('/protected')
@login_required
def protected_route():
    return render_template('protected.html')

# Token-based protection (API)
@app.route('/api/protected')
@token_required
def protected_api():
    user = request.current_user
    return jsonify({'user_id': user['user_id']})

# Role-based protection
@app.route('/api/admin')
@role_required(['admin'])
def admin_only():
    return jsonify({'message': 'Admin access granted'})
```

## Testing the System

### Test User Creation
1. Register a test user through the web interface
2. Verify the user appears in the database:
```sql
SELECT * FROM users;
```

### Test Login
1. Login with the test credentials
2. Verify you can access the dashboard
3. Check that user info appears in the sidebar

### Test Logout
1. Click the logout button in the sidebar
2. Verify you're redirected to the login page
3. Try accessing `/home` - should redirect to login

## Troubleshooting

### Issue: "Failed to connect to database"
- Check MySQL is running
- Verify database credentials in `.env` file
- Ensure `medical_prescription_db` database exists

### Issue: "Registration failed"
- Check if username/email already exists
- Verify password meets minimum requirements
- Check database connection

### Issue: "Invalid credentials"
- Verify username/email and password are correct
- Check if user account is active (`is_active = TRUE`)

### Issue: "Token verification failed"
- Token may have expired (24 hour default)
- Login again to get a new token
- Check SECRET_KEY is properly set

## Next Steps

1. **Email Verification** - Add email verification for new accounts
2. **Password Reset** - Implement forgot password functionality
3. **Profile Management** - Allow users to update their profile
4. **Admin Panel** - Create admin interface for user management
5. **Audit Logging** - Log authentication events for security

## Security Recommendations

1. Change the `SECRET_KEY` in config.py to a strong random value
2. Enable HTTPS in production
3. Implement rate limiting for login attempts
4. Add CAPTCHA for registration
5. Regular security audits
6. Keep dependencies updated

## Dependencies

Already included in requirements.txt:
- `bcrypt>=4.1.2` - Password hashing
- `PyJWT>=2.8.0` - JWT token generation
- `Flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - CORS support

---

**System Status**: ✅ Authentication system fully implemented and ready to use!

For questions or issues, refer to the project documentation or contact the development team.
