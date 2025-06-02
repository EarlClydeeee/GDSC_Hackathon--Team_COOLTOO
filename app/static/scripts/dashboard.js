// Initialize map
let incidentMap;
let markers = [];
let heatLayer;

function initMap() {
  incidentMap = L.map("incident-map").setView([14.5995, 120.9842], 11); // Center on Manila
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(incidentMap);
}

function updateMap(incidents) {
  // Clear existing markers
  markers.forEach((marker) => marker.remove());
  markers = [];

  // Clear existing heatmap
  if (heatLayer) {
    heatLayer.remove();
  }

  const heatPoints = [];

  incidents.forEach((incident) => {
    const [lat, lng] = incident.location
      .split(",")
      .map((coord) => parseFloat(coord.trim()));

    if (!isNaN(lat) && !isNaN(lng)) {
      // Add marker
      const marker = L.marker([lat, lng]).bindPopup(`
        <strong>${incident.incident_type}</strong><br>
        Priority: ${incident.priority}<br>
        Status: ${incident.status}<br>
        ${incident.description}
      `);
      marker.addTo(incidentMap);
      markers.push(marker);

      // Add to heatmap points
      heatPoints.push([lat, lng, 1]); // You can replace 1 with a weight if needed
    }
  });

  // Add heat layer
  heatLayer = L.heatLayer(heatPoints, {
    radius: 25,
    blur: 15,
    maxZoom: 17,
  }).addTo(incidentMap);

  // Fit map bounds
  if (markers.length > 0) {
    const group = new L.featureGroup(markers);
    incidentMap.fitBounds(group.getBounds());
  }
}

// Initialize charts
function initCharts(analyticsData) {
  // Priority distribution chart
  const priorityCtx = document
    .getElementById("priority-chart")
    .getContext("2d");
  new Chart(priorityCtx, {
    type: "doughnut",
    data: {
      labels: ["Low", "Medium", "High", "Urgent"],
      datasets: [
        {
          data: analyticsData.priorityDistribution,
          backgroundColor: ["#10b981", "#f59e0b", "#ef4444", "#dc2626"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });

  // Trend analysis chart
  const trendCtx = document.getElementById("trend-chart").getContext("2d");
  new Chart(trendCtx, {
    type: "line",
    data: {
      labels: analyticsData.trendLabels,
      datasets: [
        {
          label: "Incidents",
          data: analyticsData.trendData,
          borderColor: "#3b82f6",
          tension: 0.1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

// Update incident list
function updateIncidentsList(incidents) {
  const container = document.getElementById("recent-incidents-list");
  container.innerHTML = incidents
    .map(
      (incident) => `
        <li class="py-4">
            <div class="flex items-center space-x-4">
                <div class="flex-shrink-0">
                    <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-${getPriorityColor(
                      incident.priority
                    )}-100">
                        <span class="text-sm font-medium leading-none text-${getPriorityColor(
                          incident.priority
                        )}-600">
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
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium incident-priority-${
                      incident.priority
                    }">
                        ${incident.status}
                    </span>
                </div>
            </div>
        </li>
    `
    )
    .join("");
}

function getPriorityColor(priority) {
  const colors = {
    low: "green",
    medium: "yellow",
    high: "red",
    urgent: "red",
  };
  return colors[priority] || "gray";
}

// Show/hide loading indicator
function toggleLoading(show) {
  const loadingIndicator = document.getElementById("loading-indicator");
  loadingIndicator.classList.toggle("hidden", !show);
}

// Show error message
function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "max-w-7xl mx-auto px-4 py-3 mt-4";
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
  document.querySelector("main").prepend(errorDiv);
  setTimeout(() => errorDiv.remove(), 5000); // Remove after 5 seconds
}

// Initialize dashboard
document.addEventListener("DOMContentLoaded", () => {
  // Initialize map
  try {
    initTypeChart();
    initResolutionChart();
    initMap();
  } catch (error) {
    console.error("Error initializing map:", error);
    showError("Failed to initialize map. Please refresh the page.");
  }

  // Initialize filters
  document.querySelectorAll(".filter-dropdown").forEach((filter) => {
    filter.addEventListener("change", () => {
      toggleLoading(true);
      applyFilters()
        .catch((error) => {
          console.error("Error applying filters:", error);
          showError("Failed to apply filters. Please try again.");
        })
        .finally(() => toggleLoading(false));
    });
  });

  // Initialize export button
  document.getElementById("export-button").addEventListener("click", () => {
    toggleLoading(true);
    exportDashboardData()
      .catch((error) => {
        console.error("Error exporting data:", error);
        showError("Failed to export data. Please try again.");
      })
      .finally(() => toggleLoading(false));
  });

  // Load initial data
  toggleLoading(true);
  fetch("/api/dashboard/incidents")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      updateMap(data.incidents);
      updateIncidentsList(data.incidents);
      initCharts(data.analytics);
      console.log(data.incidents);
    })
    .catch((error) => {
      console.error("Error fetching initial data:", error);
      showError("Failed to load dashboard data. Please refresh the page.");
    })
    .finally(() => toggleLoading(false));
});

// Filter handling
async function applyFilters() {
  const type = document.getElementById("incident-type").value;
  const dateRange = document.getElementById("date-range").value;
  const priority = document.getElementById("priority").value;

  const response = await fetch(
    `/api/dashboard/incidents?type=${type}&dateRange=${dateRange}&priority=${priority}`
  );
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
  const type = document.getElementById("incident-type").value;
  const dateRange = document.getElementById("date-range").value;
  const priority = document.getElementById("priority").value;

  const response = await fetch(
    `/api/dashboard/export?type=${type}&dateRange=${dateRange}&priority=${priority}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Create a blob from the response and trigger download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `incidents_report_${new Date().toISOString().split("T")[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

//////////////////////////////
// Initialize report types chart
async function initResolutionChart() {
  try {
    const response = await fetch("/api/dashboard/status-summary");
    if (!response.ok) throw new Error("Failed to fetch resolution data");

    const data = await response.json(); // Assuming format: [{ status: 'Resolved', count: 12 }, ...]

    const labels = data.map((item) => item.status);
    const counts = data.map((item) => item.count);

    const resolutionCtx = document
      .getElementById("resolution-chart")
      .getContext("2d");
    new Chart(resolutionCtx, {
      type: "doughnut",
      data: {
        labels: labels, // ['Active', 'Resolved', 'Pending']
        datasets: [
          {
            data: counts, // [5, 12, 3]
            backgroundColor: [
              "#ef4444", 
              "#f59e0b", 
              "#10b981", 
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
          datalabels: {
            color: "#fff",
            font: {
              weight: "bold",
              size: 14,
            },
            formatter: (value, context) => {
              return value; // show raw number
            },
          },
        },
      },
      plugins: [ChartDataLabels], // <-- important
    });
  } catch (error) {
    console.error("Error initializing resolution chart:", error);
    showError("Failed to load resolution chart data.");
  }
}

async function initTypeChart() {
    try {
        const response = await fetch('/api/dashboard/type-summary');
        if (!response.ok) throw new Error('Failed to fetch type data');

        const data = await response.json(); // e.g., [{ type: "Theft", count: 5 }, ...]

        const labels = data.map(item => item.type);
        const counts = data.map(item => item.count);

        const ctx = document.getElementById('type-chart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Reports',
                    data: counts,
                    backgroundColor: '#3b82f6'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Report Count per Incident Type'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing type chart:', error);
        showError('Failed to load report type chart.');
    }
}