

// static/js/dashboard-refresh.js

function refreshDashboard() {
    // Add refresh animation to button
    const refreshBtn = document.querySelector('.btn-outline-primary i');
    refreshBtn.classList.add('rotate-animation');

    // Reload the page
    window.location.reload();
}

// Auto-refresh every 5 minutes
setInterval(refreshDashboard, 300000);