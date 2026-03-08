"""
Quick Test Script for Handwriting Recognition System
Run this to verify your installation is working correctly
"""

import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(test_name, passed, message=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {test_name}")
    if message:
        print(f"      {message}")

def test_imports():
    """Test if all required packages are installed"""
    print_header("Testing Package Imports")
    
    tests = {
        "Flask": "flask",
        "TensorFlow": "tensorflow",
        "OpenCV": "cv2",
        "NumPy": "numpy",
        "MySQL Connector": "mysql.connector",
        "TextBlob": "textblob",
        "Pillow": "PIL",
    }
    
    all_passed = True
    for name, module in tests.items():
        try:
            __import__(module)
            if module == "tensorflow":
                import tensorflow as tf
                version = tf.__version__
                print_status(name, True, f"Version: {version}")
            elif module == "cv2":
                import cv2
                version = cv2.__version__
                print_status(name, True, f"Version: {version}")
            else:
                print_status(name, True)
        except ImportError as e:
            print_status(name, False, str(e))
            all_passed = False
    
    return all_passed

def test_directories():
    """Test if all required directories exist"""
    print_header("Testing Directory Structure")
    
    required_dirs = [
        "backend",
        "backend/models",
        "backend/utils",
        "frontend",
        "frontend/templates",
        "frontend/static",
        "data/uploads",
        "data/processed",
        "trained_models"
    ]
    
    all_passed = True
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        print_status(dir_path, exists)
        if not exists:
            all_passed = False
    
    return all_passed

def test_files():
    """Test if all required files exist"""
    print_header("Testing Required Files")
    
    required_files = [
        "backend/app.py",
        "backend/config.py",
        "backend/models/cnn_model.py",
        "backend/utils/preprocessing.py",
        "backend/utils/segmentation.py",
        "backend/utils/postprocessing.py",
        "backend/utils/database.py",
        "frontend/templates/index.html",
        "frontend/static/css/style.css",
        "frontend/static/js/main.js",
        "requirements.txt",
        "database_schema.sql"
    ]
    
    all_passed = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print_status(file_path, exists)
        if not exists:
            all_passed = False
    
    return all_passed

def test_model_components():
    """Test if model components can be imported"""
    print_header("Testing Model Components")
    
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from models.cnn_model import CNNModel
        print_status("CNNModel Import", True)
        
        # Test model creation
        model = CNNModel(input_shape=(28, 28, 1), num_classes=62)
        print_status("CNNModel Initialization", True)
        
        # Test model building
        model.build_model(architecture='simple')
        print_status("Model Building", True)
        
        # Test model info
        info = model.get_model_size()
        print_status("Model Info", True, f"Parameters: {info['total_parameters']:,}")
        
        return True
    except Exception as e:
        print_status("Model Components", False, str(e))
        return False

def test_preprocessing():
    """Test preprocessing components"""
    print_header("Testing Preprocessing Components")
    
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from utils.preprocessing import ImagePreprocessor
        print_status("ImagePreprocessor Import", True)
        
        preprocessor = ImagePreprocessor(target_size=(28, 28))
        print_status("ImagePreprocessor Initialization", True)
        
        return True
    except Exception as e:
        print_status("Preprocessing", False, str(e))
        return False

def test_segmentation():
    """Test segmentation components"""
    print_header("Testing Segmentation Components")
    
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from utils.segmentation import TextSegmenter
        print_status("TextSegmenter Import", True)
        
        segmenter = TextSegmenter()
        print_status("TextSegmenter Initialization", True)
        
        return True
    except Exception as e:
        print_status("Segmentation", False, str(e))
        return False

def test_database():
    """Test database components"""
    print_header("Testing Database Components")
    
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from utils.database import Database
        print_status("Database Import", True)
        
        # Note: Won't test connection without credentials
        print_status("Database Class", True, "Connection test skipped (needs credentials)")
        
        return True
    except Exception as e:
        print_status("Database", False, str(e))
        return False

def test_environment():
    """Test environment configuration"""
    print_header("Testing Environment Configuration")
    
    env_file = ".env"
    env_example = ".env.example"
    
    has_example = os.path.exists(env_example)
    print_status(".env.example exists", has_example)
    
    has_env = os.path.exists(env_file)
    print_status(".env exists", has_env)
    
    if not has_env:
        print("      ⚠ Warning: .env file not found. Copy .env.example to .env")
    
    return has_example

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "SYSTEM VERIFICATION TEST" + " "*19 + "║")
    print("║" + " "*10 + "Handwriting Recognition System" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['directories'] = test_directories()
    results['files'] = test_files()
    results['model'] = test_model_components()
    results['preprocessing'] = test_preprocessing()
    results['segmentation'] = test_segmentation()
    results['database'] = test_database()
    results['environment'] = test_environment()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Configure .env with your database credentials")
        print("2. Create database: CREATE DATABASE handwriting_db;")
        print("3. Run schema: mysql -u root -p handwriting_db < database_schema.sql")
        print("4. Train model: python backend\\models\\train_model.py --synthetic")
        print("5. Start server: python backend\\app.py")
        print("6. Open browser: http://localhost:5000")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Check directory structure")
        print("- Ensure all files are present")
    
    print("\n" + "="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
