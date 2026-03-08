// Main JavaScript for Medical Prescription Recognition System

// API Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    recognize: `${API_BASE_URL}/api/recognize`,
    history: `${API_BASE_URL}/api/history`,
    search: `${API_BASE_URL}/api/search`,
    statistics: `${API_BASE_URL}/api/statistics`,
    health: `${API_BASE_URL}/api/health`
};

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const previewSection = document.getElementById('previewSection');
const imagePreview = document.getElementById('imagePreview');
const recognizeBtn = document.getElementById('recognizeBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');

// State
let selectedFile = null;
let currentResult = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadHistory();
    checkAPIHealth();
});

// Event Listeners
function initializeEventListeners() {
    // File upload events
    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // Button events
    recognizeBtn.addEventListener('click', recognizeText);
    clearBtn.addEventListener('click', clearImage);
    
    // Results events
    document.getElementById('copyBtn')?.addEventListener('click', copyText);
    document.getElementById('downloadBtn')?.addEventListener('click', downloadText);
    document.getElementById('toggleDetails')?.addEventListener('click', toggleDetails);
    
    // History events
    document.getElementById('refreshHistoryBtn')?.addEventListener('click', loadHistory);
    
    // Footer links
    document.getElementById('statsLink')?.addEventListener('click', showStatistics);
}

// File Selection Handlers
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    dropZone.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    dropZone.classList.remove('dragover');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        processFile(file);
    }
}

function processFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
        showToast('Please select a valid image file (JPG, PNG, BMP)', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File size exceeds 16MB limit', 'error');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Text Recognition
async function recognizeText() {
    if (!selectedFile) {
        showToast('Please select an image first', 'error');
        return;
    }
    
    // Show loading
    showLoading(true);
    disableButton(recognizeBtn, true);
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        // Make API request
        const response = await fetch(API_ENDPOINTS.recognize, {
            method: 'POST',
            body: formData
        });
        
        // Check for errors
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentResult = data;
            displayResults(data);
            showToast('Prescription processed successfully!', 'success');
            
            // Refresh history
            setTimeout(() => loadHistory(), 1000);
        } else {
            showToast(data.error || 'Recognition failed', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Network error. Please check your connection.', 'error');
    } finally {
        showLoading(false);
        disableButton(recognizeBtn, false);
    }
}

// Display Results
function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update statistics
    document.getElementById('confidenceValue').textContent = 
        `${(data.confidence * 100).toFixed(1)}%`;
    document.getElementById('charCount').textContent = data.num_characters;
    document.getElementById('processingTime').textContent = 
        `${data.processing_time.toFixed(2)}s`;
    
    // Update recognized text
    document.getElementById('recognizedText').textContent = data.text;
    
    // Update details
    if (data.details) {
        document.getElementById('rawText').textContent = 
            data.details.raw_text || 'N/A';
        document.getElementById('correctedText').textContent = 
            data.details.corrected_text || 'N/A';
    }
    
    document.getElementById('timestamp').textContent = 
        new Date(data.timestamp).toLocaleString();
}

// Text Actions
function copyText() {
    const text = document.getElementById('recognizedText').textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Text copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Failed to copy text', 'error');
    });
}

function downloadText() {
    const text = document.getElementById('recognizedText').textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `recognized_text_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Text downloaded successfully!', 'success');
}

function toggleDetails() {
    const detailsContent = document.getElementById('detailsContent');
    const toggleBtn = document.getElementById('toggleDetails');
    
    if (detailsContent.style.display === 'none') {
        detailsContent.style.display = 'block';
        toggleBtn.textContent = 'Hide Processing Details ▲';
    } else {
        detailsContent.style.display = 'none';
        toggleBtn.textContent = 'Show Processing Details ▼';
    }
}

// History
async function loadHistory() {
    try {
        const response = await fetch(`${API_ENDPOINTS.history}?limit=10`);
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            displayHistory(data.results);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(results) {
    const historyList = document.getElementById('historyList');
    
    if (results.length === 0) {
        historyList.innerHTML = '<p class="empty-message">No history available yet.</p>';
        return;
    }
    
    historyList.innerHTML = results.map(item => `
        <div class="history-item" onclick="showHistoryDetails(${item.id})">
            <div class="history-item-header">
                <span class="history-filename">${escapeHtml(item.original_filename)}</span>
                <span class="history-time">${formatTimeAgo(item.timestamp)}</span>
            </div>
            <div class="history-text">${escapeHtml(item.recognized_text || 'No text')}</div>
            <div class="history-stats">
                <span>📊 Confidence: ${(item.confidence_score * 100).toFixed(1)}%</span>
                <span>🔤 Characters: ${item.num_characters}</span>
                <span>⏱️ ${item.processing_time.toFixed(2)}s</span>
            </div>
        </div>
    `).join('');
}

function showHistoryDetails(recordId) {
    // You can implement a modal or expand view here
    console.log('Show details for record:', recordId);
    showToast('History details feature coming soon!', 'warning');
}

// Statistics
async function showStatistics(event) {
    event.preventDefault();
    
    try {
        const response = await fetch(API_ENDPOINTS.statistics);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.statistics;
            let message = 'System Statistics:\n\n';
            message += `Total Recognitions: ${stats.total_recognitions || 0}\n`;
            message += `Total Characters: ${stats.total_characters || 0}\n`;
            message += `Average Confidence: ${((stats.average_confidence || 0) * 100).toFixed(1)}%\n`;
            message += `Average Processing Time: ${(stats.average_processing_time || 0).toFixed(2)}s`;
            
            alert(message);
        }
    } catch (error) {
        console.error('Error fetching statistics:', error);
        showToast('Failed to load statistics', 'error');
    }
}

// API Health Check
async function checkAPIHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('✓ API is healthy');
            
            if (!data.model_loaded) {
                showToast('Warning: Model not loaded. Please train a model first.', 'warning');
            }
        }
    } catch (error) {
        console.error('API health check failed:', error);
        showToast('Cannot connect to server', 'error');
    }
}

// UI Helpers
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function disableButton(button, disable) {
    button.disabled = disable;
    
    if (disable) {
        button.querySelector('.btn-text').style.display = 'none';
        button.querySelector('.btn-loader').style.display = 'inline-flex';
    } else {
        button.querySelector('.btn-text').style.display = 'inline';
        button.querySelector('.btn-loader').style.display = 'none';
    }
}

function showToast(message, type = 'success') {
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    
    // Set message
    toastMessage.textContent = message;
    
    // Set icon based on type
    const icons = {
        success: '✓',
        error: '✗',
        warning: '⚠'
    };
    toastIcon.textContent = icons[type] || '✓';
    
    // Set class
    toast.className = `toast ${type} show`;
    
    // Auto hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTimeAgo(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// Prevent default drag and drop on page
window.addEventListener('dragover', (e) => {
    e.preventDefault();
}, false);

window.addEventListener('drop', (e) => {
    e.preventDefault();
}, false);

console.log('Handwriting Recognition System initialized');
