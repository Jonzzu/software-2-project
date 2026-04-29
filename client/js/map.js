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

    // Create marker
    const marker = L.marker([latitude, longitude]).addTo(map);

    // Create custom icon with ICAO badge
    const customIcon = L.divIcon({
        className: 'airport-marker',
        html: `<div class="airport-badge" data-icao="${icao}" data-name="${name}">${icao}</div>`,
        iconSize: [60, 30],
        iconAnchor: [30, 15]
    });

    marker.setIcon(customIcon);

    // Add click handler to badge
    setTimeout(() => {
        const badge = document.querySelector(`[data-icao="${icao}"]`);
        if (badge) {
            badge.addEventListener('click', (e) => {
                e.stopPropagation();
                openTravelModal(icao, name);
            });
        }
    }, 50);

    // Store marker for later reference
    airportMarkers[icao] = marker;
}

/**
 * Open the travel confirmation modal
 */
function openTravelModal(icao, airportName) {
    const modal = document.getElementById('travelModal');
    const modalTitle = document.querySelector('#travelModal .modal-title');

    modalTitle.textContent = airportName;
    modal.classList.add('active');

    // Remove old listeners
    const confirmBtn = document.querySelector('#travelModal .btn-confirm');
    const cancelBtn = document.querySelector('#travelModal .btn-cancel');

    confirmBtn.replaceWith(confirmBtn.cloneNode(true));
    cancelBtn.replaceWith(cancelBtn.cloneNode(true));

    // Add new listeners
    document.querySelector('#travelModal .btn-confirm').addEventListener('click', () => {
        handleTravelConfirm(icao, airportName);
    });

    document.querySelector('#travelModal .btn-cancel').addEventListener('click', () => {
        closeTravelModal();
    });
}

/**
 * Close the travel confirmation modal
 */
function closeTravelModal() {
    const modal = document.getElementById('travelModal');
    modal.classList.remove('active');
}

/**
 * Handle travel confirmation
 */
function handleTravelConfirm(icao, airportName) {
    console.log(`Travel confirmed to ${icao} (${airportName})`);
    closeTravelModal();
}

loadAirports();