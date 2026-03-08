// History Page JavaScript
// Note: API_BASE_URL is already defined in auth.js - use window.location.origin instead
const HISTORY_API_URL = window.location.origin;

let currentPage = 1;
let totalPages = 1;
const itemsPerPage = 10;
let allHistory = [];
let filteredHistory = [];

// Load history on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('History page loaded');
    loadHistory();

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filterHistory(searchTerm);
        });
    }

    // Pagination buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });
    }
});

// Load all history records
async function loadHistory() {
    try {
        console.log('Loading history from API...');
        const response = await fetch(`${HISTORY_API_URL}/api/history?limit=100`);
        console.log('Response status:', response.status);
        
        const result = await response.json();
        console.log('History data received:', result);

        if (result.success) {
            allHistory = result.data || [];
            console.log('Total history records:', allHistory.length);
            filteredHistory = [...allHistory];
            currentPage = 1;
            calculatePagination();
            renderTable();
        } else {
            console.error('API returned success=false');
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Filter history by search term
function filterHistory(searchTerm) {
    if (!searchTerm) {
        filteredHistory = [...allHistory];
    } else {
        filteredHistory = allHistory.filter(item =>
            item.original_filename?.toLowerCase().includes(searchTerm) ||
            item.recognized_text?.toLowerCase().includes(searchTerm)
        );
    }
    currentPage = 1;
    calculatePagination();
    renderTable();
}

// Calculate pagination
function calculatePagination() {
    totalPages = Math.ceil(filteredHistory.length / itemsPerPage) || 1;
}

// Render table with pagination
function renderTable() {
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';

    // Update total records count
    const totalRecordsSpan = document.getElementById('totalRecords');
    if (totalRecordsSpan) {
        totalRecordsSpan.textContent = filteredHistory.length;
    }

    if (filteredHistory.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem; color: #666;">No records found</td></tr>';
        updatePaginationControls();
        return;
    }

    const startIdx = (currentPage - 1) * itemsPerPage;
    const endIdx = Math.min(startIdx + itemsPerPage, filteredHistory.length);
    const pageItems = filteredHistory.slice(startIdx, endIdx);

    pageItems.forEach(item => {
        const row = document.createElement('tr');

        const timestamp = new Date(item.timestamp).toLocaleString();
        const confidence = Math.round((item.confidence_score || 0) * 100);

        // Convert file path to URL - extract just the filename
        const imageUrl = item.image_path ? getImageUrl(item.image_path) : null;
        const preview = imageUrl ?
            `<img src="${imageUrl}" alt="Preview" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" onerror="this.style.display='none'">` :
            '<span style="color: #999;">No preview</span>';
        const textPreview = item.recognized_text ?
            item.recognized_text.substring(0, 50) + (item.recognized_text.length > 50 ? '...' : '') :
            '<span style="color: #999;">No text</span>';

        row.innerHTML = `
            <td>${item.id}</td>
            <td>${timestamp}</td>
            <td>${item.original_filename || 'N/A'}</td>
            <td>${preview}</td>
            <td><span class="badge ${confidence > 80 ? 'badge-success' : confidence > 50 ? 'badge-warning' : 'badge-danger'}">${confidence}%</span></td>
            <td>${textPreview}</td>
            <td><span class="badge badge-info">${item.method || 'N/A'}</span></td>
            <td>
                <button class="btn-icon" onclick="viewDetails(${item.id})" title="View Details">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>
                        <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                    </svg>
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });

    updatePaginationControls();
}

// Update pagination controls
function updatePaginationControls() {
    document.getElementById('pageInfo').textContent =
        `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.getElementById('nextBtn').disabled = currentPage === totalPages;
}

// View details modal
window.viewDetails = function (id) {
    const item = allHistory.find(h => h.id === id);
    if (!item) return;

    const modal = document.getElementById('detailModal');
    const modalImage = document.getElementById('modalImage');
    const modalText = document.getElementById('modalText');
    const modalFilename = document.getElementById('modalFilename');
    const modalDate = document.getElementById('modalDate');
    const modalConfidence = document.getElementById('modalConfidence');
    const modalMethod = document.getElementById('modalMethod');

    modalFilename.textContent = item.original_filename || 'N/A';
    modalDate.textContent = new Date(item.timestamp).toLocaleString();
    modalConfidence.textContent = `${Math.round((item.confidence_score || 0) * 100)}%`;
    modalMethod.textContent = item.method || 'N/A';
    modalText.textContent = item.recognized_text || 'No text recognized';

    if (item.image_path) {
        const imageUrl = getImageUrl(item.image_path);
        modalImage.src = imageUrl;
        modalImage.style.display = 'block';
    } else {
        modalImage.style.display = 'none';
    }

    modal.style.display = 'flex';
};

// Close modal
document.getElementById('closeModal').addEventListener('click', () => {
    document.getElementById('detailModal').style.display = 'none';
});

// Close modal on outside click
window.addEventListener('click', (e) => {
    const modal = document.getElementById('detailModal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Helper function to convert file path to URL
function getImageUrl(filePath) {
    if (!filePath) return null;
    // Extract just the filename from the full path
    const filename = filePath.split(/[\\/]/).pop();
    return `/uploads/${filename}`;
}
