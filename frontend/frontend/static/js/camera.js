// Camera Page JavaScript
// Note: API_BASE_URL is already defined in auth.js - use window.location.origin instead
const CAMERA_API_URL = window.location.origin;

const video = document.getElementById('cameraView');
const canvas = document.getElementById('captureCanvas');
const startBtn = document.getElementById('startCameraBtn');
const captureBtn = document.getElementById('captureBtn');
const stopBtn = document.getElementById('stopCameraBtn');
const recognizeBtn = document.getElementById('recognizeBtn');
const retakeBtn = document.getElementById('retakeBtn');

let stream = null;
let capturedBlob = null;

// Start camera
startBtn.addEventListener('click', async () => {
    try {
        console.log('Requesting camera access...');
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment'
            }
        });
        console.log('Camera access granted');
        video.srcObject = stream;
        startBtn.style.display = 'none';
        captureBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'inline-flex';
    } catch (error) {
        console.error('Camera error:', error);
        alert('Error accessing camera: ' + error.message + '\n\nPlease make sure:\n1. You have a camera connected\n2. You granted camera permissions\n3. No other app is using the camera');
    }
});

// Capture photo
captureBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
        capturedBlob = blob;
        const url = URL.createObjectURL(blob);
        document.getElementById('capturedImage').src = url;
        document.getElementById('capturedSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
    }, 'image/jpeg', 0.95);
});

// Stop camera
stopBtn.addEventListener('click', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        startBtn.style.display = 'inline-flex';
        captureBtn.style.display = 'none';
        stopBtn.style.display = 'none';
    }
});

// Retake photo
retakeBtn.addEventListener('click', () => {
    document.getElementById('capturedSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    capturedBlob = null;
});

// Recognize text
recognizeBtn.addEventListener('click', async () => {
    if (!capturedBlob) return;

    const btnText = recognizeBtn.querySelector('.btn-text');
    const btnLoader = recognizeBtn.querySelector('.btn-loader');

    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-flex';
    recognizeBtn.disabled = true;

    try {
        const formData = new FormData();
        // Create unique filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        formData.append('image', capturedBlob, `camera-capture-${timestamp}.jpg`);

        const response = await fetch(`${CAMERA_API_URL}/api/recognize`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('confidenceValue').textContent =
                `${Math.round(result.confidence * 100)}%`;
            document.getElementById('processingTime').textContent =
                `${result.processing_time.toFixed(2)}s`;
            document.getElementById('recognizedText').textContent = result.text || 'No text recognized';
            document.getElementById('resultsSection').style.display = 'block';
        } else {
            alert('Recognition failed: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        recognizeBtn.disabled = false;
    }
});
