// Trading Dashboard JavaScript

// Fetch live market data
async function fetchMarketData(pair) {
    try {
        const response = await fetch(`/api/market-data/${pair}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching market data:', error);
        return null;
    }
}

// Update signal display
function updateSignalDisplay() {
    fetch('/api/check-signals')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                showNotification(`${data.length} new signal(s) executed!`, 'success');
                setTimeout(() => location.reload(), 2000);
            }
        });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

// Auto-refresh signals every 30 seconds
if (document.querySelector('.signals-list')) {
    setInterval(updateSignalDisplay, 30000);
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    showNotification('Copied to clipboard!', 'success');
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Load user signals
async function loadUserSignals() {
    try {
        const response = await fetch('/api/user/signals');
        const signals = await response.json();
        
        const signalList = document.getElementById('user-signals-list');
        if (signalList) {
            signalList.innerHTML = signals.map(signal => `
                <div class="signal-card">
                    <div class="row">
                        <div class="col-md-3">
                            <strong>${signal.pair}</strong>
                        </div>
                        <div class="col-md-2">
                            <span class="signal-type-${signal.type.toLowerCase()}">${signal.type}</span>
                        </div>
                        <div class="col-md-4">
                            <small>${formatDate(signal.time)}</small>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading signals:', error);
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('user-signals-list')) {
        loadUserSignals();
        setInterval(loadUserSignals, 60000);
    }
});