# Tesseract OCR Installation Guide

## What Changed?
**DeepSeek API does not support vision/image input** - it only supports text.

The system now uses:
1. **Tesseract OCR** - Free, open-source text extraction
2. **DeepSeek AI** (optional) - Text refinement for better accuracy

## Install Tesseract OCR

### Windows Installation

1. **Download Tesseract installer:**
   https://github.com/UB-Mannheim/tesseract/wiki
   
   Direct link: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

2. **Run the installer**
   - Click "Next" through the installation wizard
   - **Important:** Note the installation path (default: `C:\Program Files\Tesseract-OCR`)
   - Complete the installation

3. **Add to System PATH:**
   
   **Option A - Automatic (PowerShell as Administrator):**
   ```powershell
   $tesseractPath = "C:\Program Files\Tesseract-OCR"
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$tesseractPath", "Machine")
   ```

   **Option B - Manual:**
   - Open "Edit the system environment variables" from Start menu
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click "OK" on all windows
   - **Restart your terminal**

4. **Verify Installation:**
   ```powershell
   tesseract --version
   ```
   
   Should output something like:
   ```
   tesseract 5.3.3
   ```

## After Installation

1. **Restart your terminal** (close and reopen PowerShell)

2. **Restart the Flask server:**
   ```powershell
   cd backend
   py app.py
   ```

3. **Upload an image** - The system will now:
   - Extract text using Tesseract OCR
   - (Optional) Refine text using DeepSeek AI if API key is configured

## System Behavior

### With Tesseract Only (No API Key)
- Uses free Tesseract OCR
- Good accuracy for printed text
- Fast, no API costs
- Method: "Tesseract OCR"

### With Tesseract + DeepSeek AI (API Key configured)
- Tesseract extracts text
- DeepSeek AI corrects OCR errors
- Better accuracy
- Small API cost per image
- Method: "OCR + DeepSeek AI"

## Troubleshooting

### "Tesseract OCR not available"
- Make sure Tesseract is installed
- Check PATH environment variable includes Tesseract directory
- Restart terminal after adding to PATH

### "tesseract is not recognized as a command"
- PATH not set correctly
- Restart terminal after modifying PATH
- Try full path: `"C:\Program Files\Tesseract-OCR\tesseract.exe" --version`

### Poor OCR quality
- Use high-resolution images
- Ensure good contrast
- Use clear fonts
- Enable DeepSeek AI refinement for corrections

## API Key (Optional)

DeepSeek AI refinement requires an API key in `.env`:
```
DEEPSEEK_API_KEY=sk-a10262ee33594fd5bc381761303ca48e
```

**Without API key:** System still works with Tesseract only  
**With API key:** Better accuracy with AI-powered error correction
