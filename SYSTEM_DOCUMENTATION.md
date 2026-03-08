# Medical Prescription Scanning System

A modern web application for scanning and digitizing handwritten medical prescriptions using AI-powered OCR technology.

## 🎯 Features

### 🏠 Dashboard (Home)
- **Real-time Statistics**: View total scans, success rate, average confidence, and today's scans
- **Trend Charts**: Visualize scan activity over the last 7 days with interactive line charts
- **Confidence Distribution**: Bar chart showing confidence score distribution
- **Recent Activity**: Quick view of the 5 most recent scans

### 📸 Camera Capture
- **Live Webcam Integration**: Capture prescriptions directly using your device's camera
- **Real-time Preview**: See what the camera sees before capturing
- **Instant Recognition**: Analyze captured images immediately
- **High Resolution**: Supports up to 1280x720 resolution for optimal clarity

### 📤 Upload
- **Drag & Drop Interface**: Simply drag prescription images into the upload zone
- **File Browser**: Traditional file selection option available
- **Image Preview**: See your uploaded image before processing
- **Detailed Results**: View confidence score, processing time, and character count
- **Copy to Clipboard**: One-click copy of recognized text

### 📋 History
- **Complete Scan History**: View all past prescription scans in a paginated table
- **Search Functionality**: Filter by filename, recognized text, or method
- **Detailed View**: Click to see full details, images, and text for any scan
- **Pagination**: Navigate through large datasets efficiently (10 records per page)
- **Image Thumbnails**: Quick preview of scanned prescriptions

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Modern web browser with camera support (for camera feature)
- DeepSeek API Key

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\madhushanka\OneDrive\Desktop\DEVORA\Campus Projects\Adithya\HOSPITAL\handwriting_recognition"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL Database**
   - Ensure MySQL is running
   - Database will be created automatically on first run

4. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```env
   DEEPSEEK_API_KEY=your_api_key_here
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=medical_prescription_db
   ```

5. **Start the Application**
   ```bash
   python backend/app.py
   ```

6. **Open in Browser**
   Navigate to: `http://127.0.0.1:5000`

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask 3.0+
- **AI Engine**: DeepSeek Vision API for OCR
- **Database**: MySQL for persistent storage
- **API**: RESTful endpoints for all operations

### Frontend
- **Layout**: Fixed sidebar navigation (250px)
- **Charts**: Chart.js for data visualization
- **Camera API**: MediaDevices getUserMedia
- **Styling**: Custom CSS with responsive design

### File Structure
```
handwriting_recognition/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── models/                # Model training scripts
│   └── utils/
│       ├── database.py        # Database operations
│       ├── deepseek_vision.py # AI vision integration
│       └── preprocessing.py   # Image preprocessing
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── sidebar.css    # Navigation & layout
│   │   │   └── style.css      # Additional styles
│   │   └── js/
│   │       ├── dashboard.js   # Dashboard functionality
│   │       ├── camera.js      # Camera capture
│   │       ├── upload.js      # File upload
│   │       └── history.js     # History display
│   └── templates/
│       ├── home.html          # Dashboard page
│       ├── camera.html        # Camera page
│       ├── upload.html        # Upload page
│       └── history.html       # History page
├── data/
│   └── uploads/               # Uploaded images storage
└── requirements.txt           # Python dependencies
```

## 🔌 API Endpoints

### Pages
- `GET /` - Dashboard/Home page
- `GET /camera` - Camera capture page
- `GET /upload` - Upload page
- `GET /history` - History page

### API
- `POST /api/recognize` - Recognize text from uploaded image
  - Body: `multipart/form-data` with `image` file
  - Response: JSON with recognized text, confidence, processing time

- `GET /api/history` - Get recognition history
  - Query params: `limit` (default: 50), `offset` (default: 0)
  - Response: Paginated list of scans

- `GET /api/statistics` - Get system statistics
  - Response: Total scans, success rate, average confidence, today's scans

- `GET /api/record/<id>` - Get specific scan details
  - Response: Complete record with image path and text

- `GET /api/health` - Health check endpoint
  - Response: System status and database connectivity

## 🎨 User Interface

### Color Scheme
- **Primary**: Blue (#2563eb)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)
- **Dark**: #1e293b (sidebar background)

### Responsive Design
- **Sidebar**: Fixed 250px on desktop, collapsible on mobile
- **Main Content**: Adjusts with left margin for sidebar
- **Charts**: Responsive and maintain aspect ratio
- **Tables**: Horizontal scroll on mobile devices

## 📊 Database Schema

### Tables

#### `recognition_results`
- `id` (PRIMARY KEY)
- `upload_id` (Foreign key to uploads)
- `image_path` (varchar)
- `original_filename` (varchar)
- `recognized_text` (TEXT)
- `confidence_score` (DECIMAL)
- `processing_time` (DECIMAL)
- `num_characters` (INT)
- `method` (varchar) - Recognition method used
- `metadata` (JSON) - Additional information
- `timestamp` (DATETIME)

#### `uploads`
- `id` (PRIMARY KEY)
- `filename` (varchar)
- `file_path` (varchar)
- `file_size` (BIGINT)
- `status` (varchar)
- `upload_time` (DATETIME)

## 🔒 Security Features

- File type validation (images only)
- File size limits (16MB max)
- SQL injection prevention (parameterized queries)
- CORS configuration
- Secure file naming (prevents path traversal)

## 🧪 Testing

Test the application by:

1. **Camera Test**: Click on Camera page, grant camera permission, capture an image
2. **Upload Test**: Upload a prescription image from your computer
3. **Dashboard Test**: Check if statistics and charts load correctly
4. **History Test**: Verify all scans appear in history with correct data

## 🐛 Troubleshooting

### Camera not working
- Ensure browser has camera permission
- Check if camera is being used by another application
- Try HTTPS (some browsers require secure context for camera)

### Database connection errors
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure database user has proper permissions

### DeepSeek API errors
- Verify API key is correct
- Check internet connectivity
- Ensure API quota is not exceeded

### Images not displaying
- Check `data/uploads/` directory exists
- Verify file permissions
- Ensure correct image paths in database

## 📝 Version History

### Version 2.0 (Current)
- Complete UI redesign with sidebar navigation
- Removed authentication system
- Added dashboard with charts and statistics
- Integrated live camera capture
- Enhanced upload interface with drag-drop
- Comprehensive history view with search and pagination

### Version 1.0 (Previous)
- Basic OCR functionality
- User authentication (removed)
- Simple upload interface

## 👥 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs in terminal
3. Check browser console for JavaScript errors

## 📄 License

This project is for educational and medical assistance purposes.

---

**Built with ❤️ for better healthcare documentation**
