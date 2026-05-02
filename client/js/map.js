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
                
                // Show the series selection modal
                showSeriesModal();
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
 * Show the series selection modal
 */
async function showSeriesModal() {
    try {
        const response = await fetch('http://localhost:5000/api/anilist/random-series');
        
        if (!response.ok) {
            throw new Error('Failed to fetch random series');
        }
        
        const data = await response.json();
        
        if (!data.success || !data.series) {
            throw new Error('No series data received');
        }
        
        // Populate the modal with series options
        const seriesOptions = document.getElementById('seriesOptions');
        seriesOptions.innerHTML = '';
        
        data.series.forEach((series, index) => {
            const card = document.createElement('div');
            card.className = 'series-card';
            card.innerHTML = `
                <img src="${series.image}" alt="${series.title}" class="series-card-image">
                <div class="series-card-info">
                    <div class="series-card-title">${series.title}</div>
                    <div class="series-card-score">★ ${series.score || 'N/A'}</div>
                </div>
            `;
            
            card.addEventListener('click', () => {
                handleSeriesSelection(series, card, seriesOptions);
            });
            
            seriesOptions.appendChild(card);
        });
        
        // Show the modal
        const seriesModal = document.getElementById('seriesModal');
        seriesModal.classList.add('active');
        seriesModal.style.display = 'flex';
        seriesModal.style.zIndex = '10000';
        
        // Handle skip button
        const skipBtn = document.getElementById('skipSeriesBtn');
        skipBtn.onclick = closeSeriesModal;
        
    } catch (error) {
        console.error('Error showing series modal:', error);
    }
}

/**
 * Handle series selection
 */
function handleSeriesSelection(series, cardElement, seriesOptions) {
    // Remove previous selection
    document.querySelectorAll('.series-card.selected').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Mark this card as selected
    cardElement.classList.add('selected');
    
    // Add the series to the player's collection
    addSeriesToCollection(series);
}

/**
 * Add selected series to player's collection
 */
async function addSeriesToCollection(series) {
    try {
        const gameId = getGameId();
        const screenName = window.currentGame.screen_name;
        
        if (!gameId || !screenName) {
            throw new Error('Game information not found');
        }
        
        // First, check if collection exists, if not create it
        let collectionId = await getOrCreateCollection(screenName);
        
        if (!collectionId) {
            throw new Error('Failed to get or create collection');
        }
        
        // Add the series to the collection
        const response = await fetch('http://localhost:5000/api/collection/add-series', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                collection_id: collectionId,
                name: series.title,
                anilist_id: series.id,
                average_score: series.score || 0,
                description: series.description,
                cover_image_url: series.image
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add series to collection');
        }
        
        const data = await response.json();
        console.log('✓ Series added to collection:', data);
        
        // Close the modal after successful addition
        closeSeriesModal();
        
        // Refresh the collection display
        updateCollectionDisplay(screenName);
        
    } catch (error) {
        console.error('✗ Error adding series to collection:', error);
        alert('Failed to add series: ' + error.message);
    }
}

/**
 * Get or create collection for the player
 */
async function getOrCreateCollection(screenName) {
    try {
        // First try to get existing collections
        const getResponse = await fetch(`http://localhost:5000/api/collection/game/${screenName}`);
        const getData = await getResponse.json();
        
        if (getData.success && getData.collections && getData.collections.length > 0) {
            // Return the first collection's ID
            return getData.collections[0].id;
        }
        
        // If no collection exists, create one
        const createResponse = await fetch('http://localhost:5000/api/collection/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                screen_name: screenName
            })
        });
        
        if (!createResponse.ok) {
            const error = await createResponse.json();
            throw new Error(error.error || 'Failed to create collection');
        }
        
        const data = await createResponse.json();
        return data.collection_id;
        
    } catch (error) {
        console.error('Error getting or creating collection:', error);
        return null;
    }
}

/**
 * Close the series selection modal
 */
function closeSeriesModal() {
    const seriesModal = document.getElementById('seriesModal');
    seriesModal.classList.remove('active');
    seriesModal.style.display = 'none';
}

/**
 * Update collection display in the UI
 */
async function updateCollectionDisplay(screenName) {
    try {
        const response = await fetch(`http://localhost:5000/api/collection/game/${screenName}`);
        const data = await response.json();
        
        if (data.success && data.collections && data.collections.length > 0) {
            // Get the first collection and its series
            const collection = data.collections[0];
                const seriesResponse = await fetch(`http://localhost:5000/api/collection/${collection.id}/series`);
                const seriesData = await seriesResponse.json();
                
                if (seriesData.success && seriesData.series) {
                    // Update the collection panel
                    displayCollection(seriesData);
                }
            }
        } catch (error) {
            console.error('Error updating collection display:', error);
        }
    }

    /**
     * Display collection in the sidebar
     */
    function displayCollection(collectionData) {
        const inventorySection = document.querySelector('.inventory-section .anime-grid');
        
        if (!inventorySection) {
            console.warn('Collection panel not found');
            return;
        }
        
        // Clear existing items
        inventorySection.innerHTML = '';
        
        // Add series items
        collectionData.series.forEach(series => {
            const itemSlot = document.createElement('div');
            itemSlot.className = 'item-slot';
            itemSlot.innerHTML = `
                <img src="${series.cover_image_url}" alt="${series.name}" title="${series.name}">
            `;
            inventorySection.appendChild(itemSlot);
        });
        
        // Update section title with count
        const title = document.querySelector('.inventory-section .section-title');
        if (title) {
            title.textContent = `INVENTORY (${collectionData.series.length})`;
        }
    }

loadAirports();