# Medical Prescription Recognition System - Setup Guide

## 🏥 System Overview
Your handwriting recognition system has been successfully converted to a **Medical Prescription Recognition System** with user authentication.

## ✨ New Features Added

### 1. User Authentication System
- **User Registration** - Create accounts with username, email, password
- **User Login** - Secure JWT-based authentication
- **Role-Based Access** - Support for Doctor, Pharmacist, Staff, Admin roles
- **Session Management** - Automatic token-based session handling
- **Protected Routes** - Prescription processing requires authentication

### 2. Database Updates
- New `users` table for account management
- Updated tables to link prescriptions with users
- Support for user roles and permissions

### 3. Frontend Updates
- Login page at `/login`
- Registration page at `/register`
- User greeting and logout button on main page
- Session expiry handling with auto-redirect

## 📋 Setup Instructions

### Step 1: Update Database Schema

Run the updated database schema to create the new tables:

```bash
# Connect to MySQL
mysql -u root -p

# Run the schema file
source database_schema.sql
```

Or manually create the database:
```sql
CREATE DATABASE IF NOT EXISTS medical_prescription_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medical_prescription_db;
-- Then run the tables from database_schema.sql
```

### Step 2: Update Environment Variables

Your `.env` file has been updated with:
- `JWT_SECRET` - For token signing (change to a strong random string in production)
- `DB_NAME` - Changed to `medical_prescription_db`

**Important**: Generate a strong JWT secret:
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use any random string generator
```

Update `.env`:
```
JWT_SECRET=your-strong-random-secret-here
DB_NAME=medical_prescription_db
```

### Step 3: Install New Dependencies

Already installed:
- `PyJWT>=2.8.0` - JWT token handling
- `bcrypt>=4.1.2` - Password hashing

If needed, reinstall:
```bash
pip install -r requirements.txt
```

### Step 4: Start the Server

```bash
cd backend
python app.py
```

Server starts at: `http://localhost:5000`

## 🚀 How to Use

### First Time Setup

1. **Access the system**: Navigate to `http://localhost:5000`
2. **You'll be redirected to login** (no authentication yet)
3. **Click "Register here"** to create the first account
4. **Fill in the registration form**:
   - Username (min 3 characters)
   - Email
   - Full Name (optional)
   - Role (Doctor/Pharmacist/Staff)
   - Password (min 6 characters)
5. **Click Register** - You'll be automatically logged in
6. **Start processing prescriptions!**

### Daily Usage

1. **Login** at `/login`
2. **Upload prescription image**
3. **System processes** using Tesseract OCR + DeepSeek AI
4. **View results** with confidence scores
5. **Check history** of processed prescriptions

### User Management

**Current Features:**
- Registration with role selection
- Login with username or email
- Automatic session management
- Logout functionality

**Future Enhancements (Optional):**
- Admin panel for user management
- Password reset functionality
- User profile editing
- Audit logs

## 🔐 Security Features

1. **Password Security**
   - Bcrypt hashing with salt
   - Minimum 6 characters
   - Never stored in plaintext

2. **Token-Based Authentication**
   - JWT tokens with 24-hour expiry
   - Secure token signing
   - Automatic expiry handling

3. **Protected Routes**
   - `/api/recognize` requires authentication
   - Automatic redirect on session expiry
   - Role-based access control ready

## 📊 Database Schema Changes

### New Tables:

**users**
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Bcrypt hashed password
- `full_name` - User's full name
- `role` - doctor/pharmacist/admin/staff
- `is_active` - Account status
- `created_at` - Registration timestamp
- `last_login` - Last login timestamp

### Updated Tables:

**recognition_results**
- Added `user_id` - Links to users table
- Added `prescription_type` - Type classification
- Foreign key constraint to users

**user_uploads**
- Added `user_id` - Links to users table
- Foreign key constraint to users

## 🎯 User Roles

| Role | Description | Future Use Cases |
|------|-------------|------------------|
| **Doctor** | Medical practitioner | Write prescriptions, view all |
| **Pharmacist** | Dispense medications | Process prescriptions, verify |
| **Staff** | Administrative staff | Upload and basic processing |
| **Admin** | System administrator | User management, system config |

## 📁 File Structure Changes

### New Files Added:
```
backend/
  utils/
    auth.py                    # Authentication utilities
frontend/
  templates/
    login.html                 # Login page
    register.html              # Registration page
```

### Updated Files:
```
backend/
  app.py                       # Added auth routes
  utils/
    database.py                # Added user management methods
    __init__.py                # Exported auth functions
frontend/
  templates/
    index.html                 # Added user greeting, logout
  static/
    js/
      main.js                  # Added auth checks, token handling
database_schema.sql            # Added users table
requirements.txt               # Added PyJWT, bcrypt
.env                           # Added JWT_SECRET
```

## 🧪 Testing the System

### Test User Registration:
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "doctor1",
  "email": "doctor@hospital.com",
  "password": "secure123",
  "full_name": "Dr. John Doe",
  "role": "doctor"
}
```

### Test Login:
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "doctor1",
  "password": "secure123"
}
```

### Test Protected Route:
```
POST /api/recognize
Authorization: Bearer <your-jwt-token>
Content-Type: multipart/form-data

image: <prescription-file>
```

## 🐛 Troubleshooting

### "Authentication token is missing"
- Make sure you're logged in
- Check if token exists in localStorage
- Login again if session expired

### "Database connection error"
- Ensure MySQL is running
- Verify database name is `medical_prescription_db`
- Check DB credentials in `.env`

### "Module 'jwt' has no attribute 'encode'"
- Reinstall PyJWT: `pip uninstall PyJWT jwt; pip install PyJWT`

### "Table 'users' doesn't exist"
- Run the database schema: `source database_schema.sql`
- Or create tables manually from schema file

## 🔄 Migration from Old System

If you have existing data in `handwriting_db`:

```sql
-- Backup old data
mysqldump -u root -p handwriting_db > backup.sql

-- Import into new database (after creating users)
mysql -u root -p medical_prescription_db < backup.sql
```

**Note**: You'll need to add user_id to existing records or create a default user.

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account
- **Body**: { username, email, password, full_name?, role? }
- **Returns**: { success, user, token }

#### POST /api/auth/login
Login with credentials
- **Body**: { username/email, password }
- **Returns**: { success, user, token }

#### GET /api/auth/me
Get current user info (Protected)
- **Headers**: Authorization: Bearer <token>
- **Returns**: { success, user }

### Prescription Processing

#### POST /api/recognize (Protected)
Process prescription image
- **Headers**: Authorization: Bearer <token>
- **Body**: multipart/form-data with image file
- **Returns**: { success, text, confidence, method, ... }

## 🎉 Success!

Your system is now ready for medical prescription processing with secure user authentication!

**Next Steps:**
1. Create your first user account
2. Upload and process a prescription
3. Monitor the system logs
4. Customize roles and permissions as needed

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Check server logs in `app.log`
- Verify database connections

Enjoy your new Medical Prescription Recognition System! 🏥✨
