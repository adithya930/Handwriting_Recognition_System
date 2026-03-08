// Upload Page JavaScript
// Note: API_BASE_URL is already defined in auth.js - use window.location.origin instead
const UPLOAD_API_URL = window.location.origin;

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const recognizeBtn = document.getElementById('recognizeBtn');
const clearBtn = document.getElementById('clearBtn');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('imagePreview');
const resultsSection = document.getElementById('resultsSection');
const recognizedText = document.getElementById('recognizedText');

let selectedFile = null;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Upload page loaded');
    console.log('Browse button:', browseBtn);
    console.log('File input:', fileInput);
});

// Browse button click
if (browseBtn) {
    browseBtn.addEventListener('click', () => {
        console.log('Browse button clicked');
        if (fileInput) {
            fileInput.click();
        } else {
            console.error('File input not found');
        }
    });
} else {
    console.error('Browse button not found');
}

// File input change
if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        console.log('File selected');
        const file = e.target.files[0];
        if (file) {
            console.log('File:', file.name);
            handleFile(file);
        }
    });
}

// Drag and drop events
if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    });
}

// Handle file selection
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Recognize text from uploaded image
if (recognizeBtn) {
    recognizeBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert('Please select an image first');
            return;
        }
        
        const btnText = recognizeBtn.querySelector('.btn-text');
        const btnLoader = recognizeBtn.querySelector('.btn-loader');
        
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-flex';
        recognizeBtn.disabled = true;
        
        try {
            const formData = new FormData();
            formData.append('image', selectedFile);
            
            const response = await fetch(`${UPLOAD_API_URL}/api/recognize`, {
                method: 'POST',
                body: formData
            });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('confidenceValue').textContent = 
                `${Math.round(result.confidence * 100)}%`;
            document.getElementById('processingTime').textContent = 
                `${result.processing_time.toFixed(2)}s`;
            document.getElementById('charCount').textContent = 
                result.text ? result.text.length : 0;
            recognizedText.textContent = result.text || 'No text recognized';
            resultsSection.style.display = 'block';
        } else {
            alert('Recognition failed: ' + result.error);
        }
    } catch (error) {
        console.error('Recognition error:', error);
        alert('Error: ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        recognizeBtn.disabled = false;
    }
    });
}

// Clear selection
if (clearBtn) {
    console.log('Clear button found, attaching event listener');
    clearBtn.addEventListener('click', () => {
        console.log('Clear button clicked');
        selectedFile = null;
        fileInput.value = '';
        previewImage.src = '';
        previewSection.style.display = 'none';
        resultsSection.style.display = 'none';
    });
} else {
    console.error('Clear button not found');
}

// Copy text to clipboard
function copyToClipboard() {
    const text = recognizedText.textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('Text copied to clipboard!');
    }).catch(err => {
        alert('Failed to copy text');
    });
}
