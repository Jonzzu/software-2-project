const DEFAULT_MONEY = 500;
const STARTING_LOCATION = 'EFHK';

function showGameScreen() {
    document.getElementById('newGameScreen').classList.remove('active');
    document.getElementById('gameScreen').classList.add('active');
}

function showNewGameScreen() {
    document.getElementById('gameScreen').classList.remove('active');
    document.getElementById('newGameScreen').classList.add('active');
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }
}

function hideError() {
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) {
        errorEl.classList.add('hidden');
    }
}

function showLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.remove('hidden');
    }
}

function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.add('hidden');
    }
}

function initNewGameScreen() {
    const playerNameInput = document.getElementById('playerName');
    const startGameBtn = document.getElementById('startGameBtn');

    if (playerNameInput) {
        playerNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleStartGame();
            }
        });
    }

    if (startGameBtn) {
        startGameBtn.addEventListener('click', handleStartGame);
    }
}

async function handleStartGame() {
    try {
        hideError();
        
        const playerNameInput = document.getElementById('playerName');
        const playerName = playerNameInput ? playerNameInput.value.trim() : '';

        if (!playerName) {
            showError('Please enter a name to continue');
            return;
        }

        if (playerName.length < 2) {
            showError('Name must be at least 2 characters long');
            return;
        }

        showLoading();

        const gameData = await createNewGame(playerName, STARTING_LOCATION);

        hideLoading();
        
        showGameScreen();
        initGameDisplay(gameData);

    } catch (error) {
        hideLoading();
        showError(error.message || 'Failed to create game');
        console.error('Error creating game:', error);
    }
}

function initGameDisplay(gameData) {
    const { game, current_airport } = gameData;

    const playerNameEl = document.getElementById('statusPlayerName');
    const locationEl = document.getElementById('statusLocation');
    const pointsEl = document.getElementById('statusPoints');
    const moneyEl = document.getElementById('statusMoney');

    if (playerNameEl) playerNameEl.textContent = game.screen_name;
    if (locationEl) locationEl.textContent = current_airport.ident;
    if (pointsEl) pointsEl.textContent = game.points;
    if (moneyEl) moneyEl.textContent = game.money + ' €';

    window.currentGame = game;
    window.currentAirport = current_airport;

    initGameActions(game);

    console.log('Game display initialized');
    console.log('Current game:', game);
    console.log('Current airport:', current_airport);
}

function updateStatusDisplay(game, airport) {
    const pointsEl = document.getElementById('statusPoints');
    const moneyEl = document.getElementById('statusMoney');
    const locationEl = document.getElementById('statusLocation');

    if (pointsEl) pointsEl.textContent = game.points;
    if (moneyEl) moneyEl.textContent = game.money + ' €';
    if (locationEl) locationEl.textContent = airport.ident;

    window.currentGame = game;
    window.currentAirport = airport;
}

function initGameActions(game) {
    const quitGameBtn = document.getElementById('quitGameBtn');

    if (quitGameBtn) {
        quitGameBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to quit? Your progress will be saved.')) {
                quitGame(game.id);
            }
        });
    }

    if (typeof loadAirports === 'function') {
        setTimeout(() => {
            loadAirports();
        }, 100);
    }
}

function quitGame(gameId) {
    clearGameId();
    const playerNameInput = document.getElementById('playerName');
    if (playerNameInput) {
        playerNameInput.value = '';
    }
    window.currentGame = null;
    window.currentAirport = null;
    showNewGameScreen();
    console.log('Game quit successfully');
}

async function checkActiveGame() {
    const gameId = getGameId();

    if (gameId) {
        try {
            console.log('Resuming game:', gameId);
            const gameData = await getGameInfo(gameId);
            showGameScreen();
            initGameDisplay(gameData);
        } catch (error) {
            console.error('Failed to resume game:', error);
            clearGameId();
            showNewGameScreen();
        }
    } else {
        showNewGameScreen();
    }
}

function initApp() {
    console.log('Initializing Anime Flight Explorer...');

    if (typeof getGameId === 'undefined' || 
        typeof clearGameId === 'undefined' || 
        typeof createNewGame === 'undefined' || 
        typeof getGameInfo === 'undefined') {
        console.error('Required functions from game.js are missing');
        return;
    }

    initNewGameScreen();
    checkActiveGame();

    console.log('Application initialized successfully');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}