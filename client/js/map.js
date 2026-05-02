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

    // Create custom icon with ICAO badge - make it clickable
    const customIcon = L.divIcon({
        className: 'airport-marker',
        html: `<div class="airport-badge" style="pointer-events: all; cursor: pointer;">${icao}</div>`,
        iconSize: [60, 30],
        iconAnchor: [30, 15],
        popupAnchor: [0, -15]
    });

    // Create marker with custom icon
    const marker = L.marker([latitude, longitude], { 
        icon: customIcon,
        pane: 'markerPane'
    });

    marker.addTo(map);

    // Get the actual DOM element after it's been added to map
    const markerElement = marker.getElement();
    
    if (markerElement) {
        markerElement.style.cursor = 'pointer';
        markerElement.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            openTravelModal(icao, name);
        }, true); // Use capture phase to ensure it fires
    }

    // Also attach to marker object for safety
    marker.on('click', (e) => {
        if (e.originalEvent) {
            e.originalEvent.stopPropagation();
            e.originalEvent.preventDefault();
        }
        openTravelModal(icao, name);
    });

    // Store marker for later reference
    airportMarkers[icao] = marker;
}

/**
 * Open the travel confirmation modal
 */
function openTravelModal(icao, airportName) {
    console.log('Opening modal for:', icao, airportName);
    
    const modal = document.getElementById('travelModal');
    const modalTitle = document.querySelector('#travelModal .modal-title');

    modalTitle.textContent = airportName;
    modal.classList.add('active');
    modal.style.display = 'flex'; // Force display
    modal.style.zIndex = '10000'; // Ensure it's on top

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
    modal.style.display = 'none';
}

/**
 * Handle travel confirmation
 */
function handleTravelConfirm(icao, airportName) {
    console.log(`Travel confirmed to ${icao} (${airportName})`);
    closeTravelModal();
    
    // Call the travelToAirport function from game.js
    travelToAirport(icao).then(travelData => {
        console.log('Travel successful:', travelData);
        
        // Fetch updated game info to refresh all stats
        const gameId = getGameId();
        if (gameId) {
            getGameInfo(gameId).then(updatedGameData => {
                console.log('Updated game data:', updatedGameData);
                // Update the sidebar stats with new game info
                updateGameStats(updatedGameData);
                // Center map on new location
                if (updatedGameData.current_airport) {
                    map.setView([updatedGameData.current_airport.latitude_deg, updatedGameData.current_airport.longitude_deg], 4);
                }
            }).catch(err => {
                console.error('Failed to fetch updated game info:', err);
            });
        }
    }).catch(err => {
        console.error('Travel failed:', err);
        alert('Travel failed: ' + err.message);
    });
}

/**
 * Update game stats in the sidebar
 */
function updateGameStats(gameData) {
    console.log('Updating game stats:', gameData);
    
    if (!gameData || !gameData.game || !gameData.current_airport) {
        console.warn('Invalid game data for update:', gameData);
        return;
    }
    
    const playerNameEl = document.getElementById('statusPlayerName');
    const locationEl = document.getElementById('statusLocation');
    const pointsEl = document.getElementById('statusPoints');
    const moneyEl = document.getElementById('statusMoney');
    
    if (playerNameEl) {
        playerNameEl.textContent = gameData.game.screen_name || '-';
        console.log('Updated player name:', gameData.game.screen_name);
    }
    
    if (locationEl) {
        locationEl.textContent = gameData.current_airport.ident || '-';
        console.log('Updated location:', gameData.current_airport.ident);
    }
    
    if (pointsEl) {
        pointsEl.textContent = gameData.game.points || '0';
        console.log('Updated points:', gameData.game.points);
    }
    
    if (moneyEl) {
        moneyEl.textContent = (gameData.game.money || '0') + ' €';
        console.log('Updated money:', gameData.game.money);
    }
    
    // Also update global state
    window.currentGame = gameData.game;
    window.currentAirport = gameData.current_airport;
    
    console.log('✓ Game stats updated successfully');
}

loadAirports();