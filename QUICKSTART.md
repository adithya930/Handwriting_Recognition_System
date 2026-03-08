# Quick Start Guide - Handwriting Recognition System

## Prerequisites Checklist

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ MySQL 8.0 or higher installed and running
- ✅ pip (Python package manager) installed
- ✅ At least 2GB of free disk space
- ✅ 4GB+ RAM recommended

---

## Installation Steps

### Step 1: Navigate to Project Directory

```powershell
cd "c:\Users\madhushanka\OneDrive\Desktop\DEVORA\Campus Projects\Adithya\HOSPITAL\handwriting_recognition"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment

```powershell
.\venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes depending on your internet speed.

### Step 5: Setup MySQL Database

1. **Start MySQL Server** (if not already running)

2. **Open MySQL Command Line** or MySQL Workbench

3. **Create Database:**
```sql
CREATE DATABASE handwriting_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **Run Schema Script:**
```powershell
# Option 1: Using mysql command line
mysql -u root -p handwriting_db < database_schema.sql

# Option 2: Using MySQL Workbench
# Open database_schema.sql and execute it
```

### Step 6: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` file with your settings:
```
DB_PASSWORD=your_mysql_password
SECRET_KEY=your-random-secret-key
```

### Step 7: Train the Model (IMPORTANT)

**Option A: Quick Test with Synthetic Data** (for testing only)
```powershell
python backend\models\train_model.py --synthetic --epochs 5
```
This takes ~2-3 minutes but won't give good accuracy.

**Option B: Full Training with EMNIST** (recommended)
```powershell
# Install dataset library first
pip install tensorflow-datasets

# Train the model (takes 30-60 minutes)
python backend\models\train_model.py --architecture standard --epochs 50
```

**Option C: Download Pre-trained Model** (fastest)
- Download from: [Add your model hosting link]
- Place in: `trained_models/model_standard_best.h5`

### Step 8: Run the Application

```powershell
python backend\app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### Step 9: Open in Browser

Navigate to: **http://localhost:5000**

---

## Quick Test

1. Upload a handwritten image
2. Click "Recognize Text"
3. View the recognized text

---

## Common Issues & Solutions

### Issue 1: MySQL Connection Error
**Error:** `Error connecting to MySQL: Access denied`

**Solution:**
- Check your MySQL password in `.env` file
- Ensure MySQL server is running
- Verify database exists: `SHOW DATABASES;`

### Issue 2: Model Not Found
**Error:** `Model file not found`

**Solution:**
- Train a model using Step 7
- Or download a pre-trained model
- Verify file exists: `trained_models/model_standard_best.h5`

### Issue 3: TensorFlow Import Error
**Error:** `No module named 'tensorflow'`

**Solution:**
```powershell
pip install tensorflow==2.15.0
```

### Issue 4: Port Already in Use
**Error:** `Address already in use`

**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in backend\config.py
```

### Issue 5: OpenCV Import Error
**Solution:**
```powershell
pip install opencv-python==4.8.1.78
```

---

## Testing the System

### Test 1: API Health Check
```powershell
# In another terminal
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true
}
```

### Test 2: Upload Test Image

Create a test image with handwritten text or download sample:
- Write "Hello World" on white paper
- Take a clear photo
- Upload through the web interface

---

## Development Mode

For development with auto-reload:

1. Set DEBUG=True in `.env`

2. Run with:
```powershell
$env:FLASK_ENV="development"
python backend\app.py
```

---

## Production Deployment

### Using Waitress (Windows)

```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 backend.app:app
```

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

---

## Performance Optimization

### 1. Use GPU Acceleration (if available)

```powershell
# Uninstall CPU version
pip uninstall tensorflow

# Install GPU version
pip install tensorflow-gpu==2.15.0
```

### 2. Model Quantization

```python
# In your training script, add:
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

### 3. Enable Caching

Add to `backend/config.py`:
```python
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300
```

---

## Monitoring & Logs

### View Logs
```powershell
# Real-time log viewing
Get-Content app.log -Wait -Tail 50
```

### Database Statistics
```sql
SELECT * FROM statistics_summary;
```

---

## Backup & Maintenance

### Backup Database
```powershell
mysqldump -u root -p handwriting_db > backup_$(Get-Date -Format "yyyyMMdd").sql
```

### Clean Old Records
```sql
CALL clean_old_records(30);  -- Keep last 30 days
```

---

## Next Steps

1. **Improve Accuracy:**
   - Train with more epochs (100+)
   - Use data augmentation: `--augment`
   - Try deep architecture: `--architecture deep`

2. **Add Features:**
   - Multi-language support
   - Batch processing
   - PDF support
   - Export to Word/PDF

3. **Optimize:**
   - Add Redis caching
   - Use CDN for static files
   - Implement background task queue

---

## Support & Resources

- **Documentation:** See README.md
- **EMNIST Dataset:** https://www.nist.gov/itl/products-and-services/emnist-dataset
- **TensorFlow Tutorials:** https://www.tensorflow.org/tutorials
- **Flask Documentation:** https://flask.palletsprojects.com/

---

## Troubleshooting Commands

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# Check installed packages
pip list

# Check MySQL status
Get-Service MySQL*

# Test database connection
python -c "import mysql.connector; print('MySQL connector OK')"

# Test TensorFlow
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)"

# Test OpenCV
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

---

**🎉 Congratulations! Your handwriting recognition system is ready to use!**

For questions or issues, check the logs in `app.log` or consult the full documentation in `README.md`.
