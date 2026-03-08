# MySQL Setup Guide for Handwriting Recognition System

## Current Status ✅
- ✅ Python 3.11.9 installed
- ✅ TensorFlow 2.19.1 installed
- ✅ Pre-trained model downloaded (model_mobilenet_pretrained.h5)
- ✅ Flask server working
- ❌ MySQL not installed or not configured

## Issue
The error `1045 (28000): Access denied for user 'root'@'localhost'` indicates either:
1. MySQL is not installed
2. MySQL password is incorrect
3. MySQL service is not running

---

## Option 1: Install MySQL (If Not Installed)

### Step 1: Download MySQL
1. Go to: https://dev.mysql.com/downloads/installer/
2. Download "MySQL Installer for Windows"
3. Choose "mysql-installer-community-8.x.x.msi"

### Step 2: Install MySQL
1. Run the installer
2. Choose "Server only" or "Developer Default"
3. **IMPORTANT**: During installation, you'll be asked to set a root password
4. **Remember this password** - you'll need it for the `.env` file

### Step 3: Verify Installation
```powershell
# Add MySQL to PATH (adjust version number as needed)
$env:Path += ";C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Test connection (will prompt for password)
mysql -u root -p
```

---

## Option 2: Use SQLite Instead (No Installation Required)

If you want to skip MySQL setup, I can modify the application to use SQLite, which requires no installation:

### Advantages:
- ✅ No installation needed
- ✅ No password configuration
- ✅ Single file database
- ✅ Perfect for development/testing

### To switch to SQLite:
Just let me know and I'll update the code in 2 minutes!

---

## Option 3: Fix Existing MySQL Installation

If MySQL is already installed but password is wrong:

### Step 1: Find Your MySQL Password
Check if you saved it in:
- A password manager
- Installation notes
- Previous project files

### Step 2: Update .env File
```powershell
notepad .env
```

Change this line:
```
DB_PASSWORD=your_mysql_password
```

To your actual password:
```
DB_PASSWORD=YourActualPassword123
```

### Step 3: Test Connection
```powershell
# Test with your password
mysql -u root -p
# Enter your password when prompted
```

---

## After MySQL is Working

### Create Database
```sql
CREATE DATABASE handwriting_db;
```

### Load Schema
```powershell
mysql -u root -p handwriting_db < database_schema.sql
```

### Restart Flask
```powershell
python backend\app.py
```

---

## Quick Decision Guide

**Choose SQLite if:**
- You want to test the system immediately
- You're just learning/experimenting
- You don't want to install MySQL

**Choose MySQL if:**
- You need production-grade database
- You're deploying to a server
- You need concurrent user access

---

## What Would You Like to Do?

**Option A**: Install MySQL (15 minutes)
- Download and install from link above
- Set password during installation
- Update .env with password
- Create database

**Option B**: Switch to SQLite (2 minutes)
- No installation needed
- I'll update the code
- Start using immediately

**Option C**: Fix existing MySQL
- Find your current MySQL password
- Update .env file
- Test connection

---

## Current Configuration Files

### .env file location:
```
C:\Users\madhushanka\OneDrive\Desktop\DEVORA\Campus Projects\Adithya\HOSPITAL\handwriting_recognition\.env
```

### What needs updating in .env:
```env
DB_PASSWORD=your_mysql_password  ← Change this to your actual MySQL password
```

### Model configuration (already fixed):
```env
MODEL_PATH=trained_models/model_mobilenet_pretrained.h5  ← ✅ Correct
```

---

## Next Steps Summary

1. **Decide**: MySQL or SQLite?
2. **If MySQL**: 
   - Install (if needed) or find password
   - Update `.env` with correct password
   - Run MySQL commands to create database
3. **If SQLite**:
   - Tell me to switch to SQLite
   - I'll update the code
4. **Restart Flask server**
5. **Test at http://localhost:5000** ✅

---

## Need Help?

Just tell me:
- "Install MySQL" → I'll guide you step-by-step
- "Use SQLite" → I'll convert the code now
- "My MySQL password is XXX" → I'll update .env for you
