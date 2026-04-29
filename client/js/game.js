// ============================================
// Game State Management & Storage
// ============================================

const GAME_STORAGE_KEY = 'currentGameId';

/**
 * Save game ID to localStorage
 * @param {number} gameId - The game ID to save
 */
function saveGameId(gameId) {
    try {
        localStorage.setItem(GAME_STORAGE_KEY, gameId);
        console.log('✓ Game ID saved to localStorage:', gameId);
    } catch (error) {
        console.error('✗ Error saving game ID:', error.message);
    }
}

/**
 * Retrieve game ID from localStorage
 * @returns {string|null} The saved game ID, or null if not found
 */
function getGameId() {
    try {
        const gameId = localStorage.getItem(GAME_STORAGE_KEY);
        if (gameId) {
            console.log('✓ Game ID retrieved from localStorage:', gameId);
        }
        return gameId;
    } catch (error) {
        console.error('✗ Error retrieving game ID:', error.message);
        return null;
    }
}

/**
 * Clear game ID from localStorage
 * Use this when starting a new game or when the player quits
 */
function clearGameId() {
    try {
        localStorage.removeItem(GAME_STORAGE_KEY);
        console.log('✓ Game ID cleared from localStorage');
    } catch (error) {
        console.error('✗ Error clearing game ID:', error.message);
    }
}

/**
 * Check if a game is currently active (ID saved in localStorage)
 * @returns {boolean} True if a game ID exists
 */
function isGameActive() {
    return getGameId() !== null;
}

// ============================================
// Game Creation
// ============================================

async function createNewGame(screenName, location = "EFHK") {
    try {
        const payload = {
            screen_name: screenName
        };
    
        if (location) {
            payload.location = location;
        }
    
        const response = await fetch('/api/game/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
    
        const data = await response.json();
    
        if (!response.ok) {
            throw new Error(data.error || 'Failed to create game');
        }
    
        console.log('✓ Game created successfully:', data);
        
        // Save the game ID to localStorage for later use
        saveGameId(data.game_id);
        
        return data;
    } catch (error) {
        console.error('✗ Error creating game:', error.message);
        throw error;
    }
}

/**
 * Fetch game information including current location details
 * @param {number} gameId - The game ID to fetch
 * @returns {Promise<Object>} Game and airport data
 */
async function getGameInfo(gameId) {
    try {
        const response = await fetch(`/api/game/${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch game info');
        }
        
        console.log('✓ Game info fetched:', data.game);
        console.log('✓ Current airport:', data.current_airport);
        return data;
    } catch (error) {
        console.error('✗ Error fetching game:', error.message);
        throw error;
    }
}