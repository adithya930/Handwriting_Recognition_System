// Dashboard JavaScript
// Define base URL for dashboard API calls
const DASHBOARD_API_URL = window.location.origin;

// Store chart instances globally
let trendsChartInstance = null;
let confidenceChartInstance = null;

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    loadDashboard(); // Load everything in one go
    loadRecentActivity();
});

// Load dashboard (stats + charts together)
async function loadDashboard() {
    try {
        console.log('Loading dashboard data...');
        console.log('API URL:', `${DASHBOARD_API_URL}/api/statistics`);
        
        const response = await fetch(`${DASHBOARD_API_URL}/api/statistics`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            console.error('Statistics API returned error:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            displayErrorState();
            return;
        }

        const data = await response.json();
        console.log('Statistics data received from server:', JSON.stringify(data, null, 2));

        if (data.success && data.statistics) {
            const stats = data.statistics;
            console.log('Stats object:', JSON.stringify(stats, null, 2));
            
            // Update stats cards
            updateStatsCards(stats);
            
            // Update charts
            renderTrendsChart(stats.trends || {});
            renderConfidenceChart(stats.confidence_distribution || {});
        } else {
            console.warn('Statistics API returned success=false or no statistics:', data);
            displayErrorState();
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        console.error('Error stack:', error.stack);
        displayErrorState();
    }
}

// Update statistics cards
function updateStatsCards(stats) {
    console.log('Updating stats cards with:', stats);
    console.log('total_scans:', stats.total_scans);
    console.log('success_rate:', stats.success_rate);
    console.log('average_confidence:', stats.average_confidence);
    console.log('today_scans:', stats.today_scans);
    
    // Update DOM elements
    const totalScansEl = document.getElementById('totalScans');
    const successRateEl = document.getElementById('successRate');
    const avgConfidenceEl = document.getElementById('avgConfidence');
    const todayScansEl = document.getElementById('todayScans');
    
    console.log('DOM elements found:', {
        totalScans: !!totalScansEl,
        successRate: !!successRateEl,
        avgConfidence: !!avgConfidenceEl,
        todayScans: !!todayScansEl
    });
    
    if (totalScansEl) totalScansEl.textContent = stats.total_scans || 0;
    if (successRateEl) successRateEl.textContent = stats.success_rate ?
        `${Math.round(stats.success_rate)}%` : '0%';
    if (avgConfidenceEl) avgConfidenceEl.textContent = stats.average_confidence ?
        `${Math.round(stats.average_confidence * 100)}%` : '0%';
    if (todayScansEl) todayScansEl.textContent = stats.today_scans || 0;
    
    console.log('Statistics cards updated successfully');
    console.log('Updated values:', {
        totalScans: totalScansEl?.textContent,
        successRate: successRateEl?.textContent,
        avgConfidence: avgConfidenceEl?.textContent,
        todayScans: todayScansEl?.textContent
    });
}

// Display error state
function displayErrorState() {
    document.getElementById('totalScans').textContent = '--';
    document.getElementById('successRate').textContent = '--';
    document.getElementById('avgConfidence').textContent = '--';
    document.getElementById('todayScans').textContent = '--';
    renderTrendsChart({});
    renderConfidenceChart({});
}

// Render trends chart
function renderTrendsChart(trends) {
    const canvas = document.getElementById('trendsChart');
    if (!canvas) {
        console.error('Trends chart canvas not found');
        return;
    }

    // Destroy existing chart instance
    if (trendsChartInstance !== null) {
        trendsChartInstance.destroy();
        trendsChartInstance = null;
    }

    const last7Days = getLast7Days();
    const scanCounts = last7Days.map(day => trends[day] || 0);

    const ctx = canvas.getContext('2d');
    trendsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days.map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
            datasets: [{
                label: 'Scans',
                data: scanCounts,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

// Render confidence distribution chart
function renderConfidenceChart(distribution) {
    const canvas = document.getElementById('confidenceChart');
    if (!canvas) {
        console.error('Confidence chart canvas not found');
        return;
    }

    // Destroy existing chart instance
    if (confidenceChartInstance !== null) {
        confidenceChartInstance.destroy();
        confidenceChartInstance = null;
    }

    const ranges = distribution && Object.keys(distribution).length > 0 ? distribution : {
        '0-20%': 0,
        '20-40%': 0,
        '40-60%': 0,
        '60-80%': 0,
        '80-100%': 0
    };

    const ctx = canvas.getContext('2d');
    confidenceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(ranges),
            datasets: [{
                label: 'Scans',
                data: Object.values(ranges),
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#eab308',
                    '#84cc16',
                    '#10b981'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch(`${DASHBOARD_API_URL}/api/history?limit=5`);
        const data = await response.json();

        if (data.success && data.data && data.data.length > 0) {
            const tbody = document.getElementById('recentActivity');
            tbody.innerHTML = data.data.map(r => `
                <tr>
                    <td>${new Date(r.timestamp).toLocaleString()}</td>
                    <td>${r.original_filename || 'Unknown'}</td>
                    <td>${r.confidence_score ? `${Math.round(r.confidence_score * 100)}%` : 'N/A'}</td>
                    <td><span class="badge badge-success">Completed</span></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

// Helper: Get last 7 days
function getLast7Days() {
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toISOString().split('T')[0]);
    }
    return days;
}