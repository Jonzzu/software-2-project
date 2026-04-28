// Initialize map centered on Europe
const map = L.map('map').setView([54.5260, 15.2551], 4);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

// Store markers for later reference
const airportMarkers = {};

/**
 * Fetch airports from backend and add them as markers
 */
async function loadAirports() {
    try {
        const response = await fetch('http://localhost:5000/api/map/airports');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success || !data.airports) {
            console.error('Failed to load airports:', data);
            return;
        }

        // Add each airport as a marker
        data.airports.forEach(airport => {
            addAirportMarker(airport);
        });

        console.log(`✓ Loaded ${data.count} airports`);
    } catch (error) {
        console.error('Error loading airports:', error);
    }
}

/**
 * Add a single airport marker to the map
 */
function addAirportMarker(airport) {
    const { name, icao, latitude, longitude } = airport;

    // Create marker with ICAO code as label
    const marker = L.marker([latitude, longitude], {
        title: name
    }).addTo(map);

    // Create popup content
    const popupContent = `
        <div class="airport-popup">
            <strong>${icao}</strong><br/>
            ${name}
        </div>
    `;

    // Bind popup to marker
    marker.bindPopup(popupContent);

    // Show popup on hover (desktop)
    marker.on('mouseover', function() {
        this.openPopup();
    });

    marker.on('mouseout', function() {
        this.closePopup();
    });

    // Show popup on click (mobile)
    marker.on('click', function() {
        this.openPopup();
    });

    // Add label to marker using custom HTML
    const customIcon = L.divIcon({
        className: 'airport-marker',
        html: `<div class="airport-label">${icao}</div>`,
        iconSize: [60, 30],
        iconAnchor: [30, 15]
    });

    marker.setIcon(customIcon);

    // Store marker for later reference
    airportMarkers[icao] = marker;
}

/**
 * Get a marker by ICAO code
 */
function getMarker(icao) {
    return airportMarkers[icao];
}

/**
 * Highlight a marker
 */
function highlightMarker(icao) {
    const marker = getMarker(icao);
    if (marker) {
        marker.openPopup();
    }
}

// Load airports when page loads
document.addEventListener('DOMContentLoaded', loadAirports);