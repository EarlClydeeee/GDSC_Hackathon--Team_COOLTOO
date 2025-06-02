// Initialize map
let incidentMap;
let markers = [];

function initMap() {
    incidentMap = L.map('incident-map').setView([14.5995, 120.9842], 11); // Center on Manila
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(incidentMap);
}

function updateMap(incidents) {
    // Clear existing markers
    markers.forEach(marker => marker.remove());
    markers = [];

    incidents.forEach(incident => {
        const [lat, lng] = incident.location.split(',').map(coord => parseFloat(coord.trim()));
        if (!isNaN(lat) && !isNaN(lng)) {
            const marker = L.marker([lat, lng])
                .bindPopup(`
                    <strong>${incident.incident_type}</strong><br>
                    Priority: ${incident.priority}<br>
                    Status: ${incident.status}<br>
                    ${incident.description}
                `);
            
            markers.push(marker);
            marker.addTo(incidentMap);
        }
    });

    // Adjust map view to fit all markers
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        incidentMap.fitBounds(group.getBounds());
    }
}

// Initialize charts
function initCharts(analyticsData) {
    // Priority distribution chart
    const priorityCtx = document.getElementById('priority-chart').getContext('2d');
    new Chart(priorityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High', 'Urgent'],
            datasets: [{
                data: analyticsData.priorityDistribution,
                backgroundColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#dc2626'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Trend analysis chart
    const trendCtx = document.getElementById('trend-chart').getContext('2d');
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: analyticsData.trendLabels,
            datasets: [{
                label: 'Incidents',
                data: analyticsData.trendData,
                borderColor: '#3b82f6',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Update incident list
function updateIncidentsList(incidents) {
    const container = document.getElementById('recent-incidents-list');
    container.innerHTML = incidents.map(incident => `
        <li class="py-4">
            <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                    <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-${getPriorityColor(incident.priority)}-100">
                        <span class="text-sm font-medium leading-none text-${getPriorityColor(incident.priority)}-600">
                            ${incident.priority.charAt(0).toUpperCase()}
                        </span>
                    </span>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                        ${incident.incident_type}
                    </p>
                    <p class="text-sm text-gray-500 truncate">
                        Location: ${incident.location}
                    </p>
                </div>
                <div>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium incident-priority-${incident.priority}">
                        ${incident.status}
                    </span>
                </div>
            </div>
        </li>
    `).join('');
}

function getPriorityColor(priority) {
    const colors = {
        low: 'green',
        medium: 'yellow',
        high: 'red',
        urgent: 'red'
    };
    return colors[priority] || 'gray';
}

// Show/hide loading indicator
function toggleLoading(show) {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.classList.toggle('hidden', !show);
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'max-w-7xl mx-auto px-4 py-3 mt-4';
    errorDiv.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">Error</h3>
                    <p class="mt-2 text-sm text-red-700">${message}</p>
                </div>
            </div>
        </div>
    `;
    document.querySelector('main').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000); // Remove after 5 seconds
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Initialize map
    try {
        initMap();
    } catch (error) {
        console.error('Error initializing map:', error);
        showError('Failed to initialize map. Please refresh the page.');
    }
    
    // Initialize filters
    document.querySelectorAll('.filter-dropdown').forEach(filter => {
        filter.addEventListener('change', () => {
            toggleLoading(true);
            applyFilters().catch(error => {
                console.error('Error applying filters:', error);
                showError('Failed to apply filters. Please try again.');
            }).finally(() => toggleLoading(false));
        });
    });

    // Initialize export button
    document.getElementById('export-button').addEventListener('click', () => {
        toggleLoading(true);
        exportDashboardData().catch(error => {
            console.error('Error exporting data:', error);
            showError('Failed to export data. Please try again.');
        }).finally(() => toggleLoading(false));
    });

    // Load initial data
    toggleLoading(true);
    fetch('/api/dashboard/incidents')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateMap(data.incidents);
            updateIncidentsList(data.incidents);
            initCharts(data.analytics);
        })
        .catch(error => {
            console.error('Error fetching initial data:', error);
            showError('Failed to load dashboard data. Please refresh the page.');
        })
        .finally(() => toggleLoading(false));
});

// Filter handling
async function applyFilters() {
    const type = document.getElementById('incident-type').value;
    const dateRange = document.getElementById('date-range').value;
    const priority = document.getElementById('priority').value;

    const response = await fetch(`/api/dashboard/incidents?type=${type}&dateRange=${dateRange}&priority=${priority}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    updateMap(data.incidents);
    updateIncidentsList(data.incidents);
    initCharts(data.analytics);
}

// Export functionality
async function exportDashboardData() {
    const type = document.getElementById('incident-type').value;
    const dateRange = document.getElementById('date-range').value;
    const priority = document.getElementById('priority').value;

    const response = await fetch(`/api/dashboard/export?type=${type}&dateRange=${dateRange}&priority=${priority}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Create a blob from the response and trigger download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incidents_report_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
