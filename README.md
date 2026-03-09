# Handwriting Recognition System

## System Architecture

This is a complete end-to-end handwriting recognition system that converts handwritten text from images into digital text using deep learning.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  (HTML/CSS/JavaScript - Image Upload Interface)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Request (Image)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Backend (API)                         │
│  - Image Upload Handler                                          │
│  - API Endpoints (/upload, /recognize, /history)                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Image Preprocessing Module                     │
│  - Noise Removal (Gaussian Blur, Morphological Operations)      │
│  - Binarization (Otsu's Thresholding, Adaptive Thresholding)   │
│  - Skew Correction & Normalization                              │
│  - Resizing & Padding                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Segmentation Module                           │
│  - Line Segmentation (Horizontal Projection)                    │
│  - Word Segmentation (Vertical Projection)                      │
│  - Character Segmentation (Connected Component Analysis)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CNN-Based Character Recognition                     │
│  - Model: Deep CNN (Conv2D + MaxPooling + Dense)               │
│  - Framework: TensorFlow/Keras                                   │
│  - Training: EMNIST/IAM Dataset                                 │
│  - Output: Character Predictions + Confidence Scores            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Post-Processing Module                         │
│  - Text Assembly (Characters → Words → Sentences)               │
│  - Spell Correction (Python enchant/TextBlob)                   │
│  - Formatting & Error Handling                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MySQL Database                              │
│  - Store: Original Image Path, Recognized Text, Timestamp       │
│  - Tables: recognition_results, user_uploads                    │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Response to Frontend                          │
│  JSON: {text: "...", confidence: 0.95, timestamp: "..."}        │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Python 3.8+**
- **TensorFlow 2.x / Keras** - Deep learning framework
- **OpenCV** - Image processing
- **NumPy** - Numerical operations
- **Flask** - Web framework
- **MySQL Connector** - Database connectivity
- **Pillow** - Image handling
- **TextBlob** - Spell correction

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript (Vanilla)** - Interactivity
- **Fetch API** - Backend communication

### Database
- **MySQL 8.0+**

## Project Structure

```
handwriting_recognition/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cnn_model.py          # CNN architecture definition
│   │   └── train_model.py        # Model training script
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── preprocessing.py      # Image preprocessing functions
│   │   ├── segmentation.py       # Text segmentation functions
│   │   ├── postprocessing.py     # Spell correction & formatting
│   │   └── database.py           # Database operations
│   ├── app.py                    # Flask application
│   └── config.py                 # Configuration settings
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── templates/
│       └── index.html
├── data/
│   ├── uploads/                  # User uploaded images
│   └── processed/                # Processed images
├── trained_models/               # Saved trained models
├── requirements.txt
├── database_schema.sql
├── train.py                      # Script to train the model
└── README.md
```

## Features

1. **Image Upload**: Drag-and-drop or file browser interface
2. **Preprocessing**: Automatic noise reduction and enhancement
3. **Segmentation**: Intelligent line, word, and character detection
4. **Recognition**: CNN-based character recognition with 90%+ accuracy
5. **Post-processing**: Spell correction and text formatting
6. **History**: Store and retrieve recognition history
7. **Confidence Scores**: Display recognition confidence for each character
8. **Multi-format Support**: JPG, PNG, BMPG formats

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project
```bash
cd handwriting_recognition
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database
1. Start MySQL server
2. Create database:
```sql
CREATE DATABASE handwriting_db;
```
3. Run the schema:
```bash
mysql -u root -p handwriting_db < database_schema.sql
```

### Step 5: Configure Database Connection
Edit `.env` with your MySQL credentials (XAMPP default uses empty password):
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=handwriting_db
```

### Step 6: Download or Train the Model

**Option A: Train from scratch (Recommended for learning)**
```bash
python train.py
```
This will train on EMNIST dataset and save the model to `trained_models/`

**Option B: Use pre-trained model**
- Install env loader (once):
```powershell
python -m pip install python-dotenv
```
- Download the MobileNetV2-based pre-trained model:
```powershell
python setup_pretrained_keras.py
```
- Point the app to the model in `.env` (already set by default):
```env
MODEL_PATH=trained_models/model_mobilenet_pretrained.h5
```
- Notes:
        - No dataset download needed for this option.
        - The pipeline automatically converts 28x28 grayscale character crops
                to 224x224 RGB for MobileNetV2 at inference time.
 - IMPORTANT: The downloaded model head is NOT trained on handwriting yet, so predictions will be low confidence ("?"). To obtain real characters you must fine‑tune:
        1. Install a dataset provider (pick one):
                ```powershell
                python -m pip install tensorflow-datasets
                # OR
                python -m pip install extra-keras-datasets
                ```
        2. Run transfer learning (memory‑safe, streamed preprocessing):
                ```powershell
                # Start small to validate, then scale up
                python backend\models\fine_tune_mobilenet.py --epochs 3 --subset 8000 --val-subset 2000 --unfreeze-last 10
                # If stable, try a larger subset later (e.g. 20000 or 40000)
                ```
                The script now uses tf.data streaming to avoid OOM while resizing to 224x224.
        3. Update `.env` to use the trained model:
                ```env
                MODEL_PATH=trained_models/model_mobilenet_transfer_best.h5
                ```
        4. Restart the app:
                ```powershell
                python backend\app.py
                ```
        5. Verify on a clear image with a few large characters first.

### Step 7: Run the Application
```bash
python backend/app.py
```
The server will start at: `http://localhost:5000`

## Usage

1. Open browser and navigate to `http://localhost:5000`
2. Upload a handwritten image (JPG, PNG, BMP)
3. Click "Recognize Text"
4. View the recognized text and confidence score
5. Results are automatically saved to database

## API Endpoints

### POST /api/recognize
Upload and recognize handwritten text
- **Input**: FormData with 'image' file
- **Output**: JSON with recognized text and metadata

```json
{
  "success": true,
  "text": "Hello World",
  "confidence": 0.95,
  "timestamp": "2025-11-18 10:30:00",
  "processing_time": 2.3
}
```

### GET /api/history
Retrieve recognition history
- **Output**: JSON array of past recognitions

### GET /api/health
Check API health status

## Model Architecture

```
Input Image (28x28x1)
        ↓
Conv2D (32 filters, 3x3) + ReLU
        ↓
MaxPooling2D (2x2)
        ↓
Conv2D (64 filters, 3x3) + ReLU
        ↓
MaxPooling2D (2x2)
        ↓
Conv2D (128 filters, 3x3) + ReLU
        ↓
MaxPooling2D (2x2)
        ↓
Flatten
        ↓
Dense (256) + ReLU + Dropout(0.5)
        ↓
Dense (128) + ReLU + Dropout(0.3)
        ↓
Dense (62) + Softmax [A-Z, a-z, 0-9]
```

## Performance Optimization Tips

### 1. Improve Accuracy
- **Use larger training dataset**: EMNIST (800k+ samples) or IAM Handwriting Database
- **Data augmentation**: Rotation, scaling, shearing during training
- **Ensemble models**: Combine multiple CNN architectures
- **Transfer learning**: Use pre-trained models (VGG, ResNet) as base
- **LSTM/RNN integration**: For context-aware word recognition

### 2. Speed Optimization
- **Model quantization**: Reduce model size by 4x with minimal accuracy loss
- **Batch processing**: Process multiple characters simultaneously
- **GPU acceleration**: Use TensorFlow GPU for 10-100x speedup
- **Caching**: Store frequently recognized patterns
- **Async processing**: Use Celery for background jobs

### 3. Preprocessing Enhancement
- **Adaptive thresholding**: Better for varying lighting conditions
- **Skew correction**: Use Hough transform
- **Noise removal**: Bilateral filtering preserves edges
- **Contrast enhancement**: CLAHE (Contrast Limited Adaptive Histogram Equalization)

### 4. Segmentation Improvement
- **Connected component analysis**: Better character isolation
- **Contour detection**: More accurate boundaries
- **Vertical projection**: Improved word spacing detection
- **Machine learning-based segmentation**: Use U-Net for complex layouts

### 5. Database Optimization
- **Indexing**: Add indexes on timestamp and user_id columns
- **Connection pooling**: Reuse database connections
- **Caching layer**: Redis for frequent queries
- **Async writes**: Queue database operations

## Advanced Features to Add

1. **Multi-language Support**: Train models for different languages
2. **Handwriting Style Recognition**: Identify individual writing patterns
3. **Real-time Recognition**: WebSocket-based live processing
4. **Mobile App**: React Native or Flutter frontend
5. **Cloud Deployment**: Docker + Kubernetes + AWS/Azure
6. **PDF Support**: Extract and recognize text from PDF documents
7. **Batch Processing**: Upload multiple images
8. **Export Options**: Export to PDF, DOCX, TXT

## Troubleshooting

### Model doesn't load
- Ensure trained model exists in `trained_models/`
- Check TensorFlow version compatibility

### Low accuracy
- Verify image quality (clear, high contrast)
- Retrain with more data
- Adjust preprocessing parameters

### Database connection fails
- Verify MySQL is running
- Check credentials in `config.py`
- Ensure database exists

### Image upload fails
- Check file size limit (default 16MB)
- Verify supported formats (JPG, PNG, BMP)
- Check folder permissions for `data/uploads/`

## Contributing

Feel free to enhance this system by:
- Adding more preprocessing techniques
- Implementing attention mechanisms
- Adding support for cursive writing
- Improving the UI/UX

## License

This project is for educational purposes.

## References

- EMNIST Dataset: https://www.nist.gov/itl/products-and-services/emnist-dataset
- IAM Handwriting Database: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database
- TensorFlow Documentation: https://www.tensorflow.org/
- OpenCV Tutorials: https://docs.opencv.org/

![image alt](https://github.com/adithya930/Handwriting_Recognition_System/blob/ef0d1a1081033c5319a6c951b694489c0592a39d/welcome%20page.png)
