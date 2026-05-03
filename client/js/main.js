const API_BASE_URL = 'http://localhost:5000';
const INVENTORY_SLOT_COUNT = 6;
const COLLECTION_STORAGE_KEY = 'animeCollection';
const GAME_STATE_STORAGE_KEY = 'animeFlightGameState';
const LEADERBOARD_STORAGE_KEY = 'animeFlightLeaderboard';
const LEADERBOARD_LIMIT = 10;
const INITIAL_FUEL = 5000;
const INITIAL_MONEY = 100;
const FUEL_PER_KM = 0.2;

let inventoryAnime = [];
let collectedAnime = loadStoredCollection();
let gameState = loadStoredGameState();
let leaderboard = loadStoredLeaderboard();
let hasAskedPlayerName = false;

async function loadRandomAnimeInventory() {
    const inventory = document.getElementById('anime-inventory');

    if (!inventory) {
        return;
    }

    if (!hasAskedPlayerName && !gameState.gameOver) {
        hasAskedPlayerName = true;
        setupPlayerNameModal(true);
    } else {
        setupPlayerNameModal();
    }
    setupNewRunButton();
    renderGameStatus();
    renderCollection();

    if (gameState.gameOver) {
        saveFinishedRunToLeaderboard();
        renderLeaderboard();
        renderAnimeInventory();
        return;
    }

    renderLeaderboard();

    try {
        const response = await fetch(`${API_BASE_URL}/api/anilist/random?count=${INVENTORY_SLOT_COUNT}`);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to load random anime');
        }

        inventoryAnime = (data.anime || []).map(addAnimePrice);
        renderAnimeInventory();
    } catch (error) {
        console.error('Error loading anime inventory:', error);
        inventoryAnime = [];
        renderAnimeInventory();
    }
}

function renderAnimeInventory() {
    const inventory = document.getElementById('anime-inventory');

    inventory.innerHTML = '';

    for (let i = 0; i < INVENTORY_SLOT_COUNT; i++) {
        const anime = inventoryAnime[i];
        inventory.appendChild(createAnimeSlot(anime, () => collectAnime(i)));
    }
}

function collectAnime(index) {
    const anime = inventoryAnime[index];

    if (!anime || gameState.gameOver) {
        return;
    }

    const price = getAnimePrice(anime);

    if (gameState.money < price) {
        gameState.money = 0;
        endGame('Money ran out');
        return;
    }

    gameState.money -= price;
    collectedAnime.push(anime);
    inventoryAnime.splice(index, 1);
    saveStoredGameState();
    saveStoredCollection();
    renderGameStatus();
    renderAnimeInventory();
    renderCollection();

    if (gameState.money <= 0) {
        endGame('Money ran out');
    }
}

function renderCollection() {
    const collection = document.getElementById('anime-collection');
    const empty = document.getElementById('collection-empty');
    const points = document.getElementById('points-val');

    if (!collection || !empty || !points) {
        return;
    }

    collection.innerHTML = '';
    empty.hidden = collectedAnime.length > 0;

    collectedAnime.forEach((anime) => {
        collection.appendChild(createCollectionRow(anime));
    });

    points.textContent = String(calculateCollectionPoints());
}

function createAnimeSlot(anime, onClick) {
    const slot = document.createElement('button');
    slot.className = 'item-slot anime-slot';
    slot.type = 'button';

    if (!anime) {
        slot.disabled = true;
        return slot;
    }

    slot.title = anime.title;
    slot.disabled = gameState.gameOver;
    slot.addEventListener('click', onClick);

    if (anime.image) {
        const image = document.createElement('img');
        image.src = anime.image;
        image.alt = anime.title;
        slot.appendChild(image);
    }

    const badge = document.createElement('span');
    badge.className = 'hidden-score-badge';
    badge.textContent = `${getAnimePrice(anime)}€`;
    slot.appendChild(badge);

    return slot;
}

function createCollectionRow(anime) {
    const row = document.createElement('tr');
    const animeCell = document.createElement('td');
    const averageCell = document.createElement('td');
    const priceCell = document.createElement('td');
    const pointsCell = document.createElement('td');
    const animeInfo = document.createElement('div');
    const score = getAnimeScore(anime);

    animeInfo.className = 'collection-anime';
    animeInfo.addEventListener('click', () => showAnimeDetails(anime));

    if (anime.image) {
        const image = document.createElement('img');
        image.src = anime.image;
        image.alt = anime.title;
        animeInfo.appendChild(image);
    }

    const title = document.createElement('div');
    title.className = 'collection-title';
    title.textContent = anime.title;

    animeInfo.appendChild(title);
    animeCell.appendChild(animeInfo);
    averageCell.textContent = String(score);
    priceCell.textContent = `${getAnimePrice(anime)}€`;
    pointsCell.textContent = String(score);

    row.appendChild(animeCell);
    row.appendChild(averageCell);
    row.appendChild(priceCell);
    row.appendChild(pointsCell);

    return row;
}

function showAnimeDetails(anime) {
    const modal = document.getElementById('animeDetailModal');
    const title = document.getElementById('anime-detail-title');
    const image = document.getElementById('anime-detail-image');
    const description = document.getElementById('anime-detail-description');
    const closeBtn = document.getElementById('anime-detail-close');

    if (!modal || !title || !image || !description || !closeBtn) {
        return;
    }

    title.textContent = anime.title;
    image.src = anime.image || '';
    image.alt = anime.title;
    description.innerHTML = anime.description || 'No description available.';

    modal.classList.add('active');

    closeBtn.onclick = () => {
        modal.classList.remove('active');
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    };
}

function calculateCollectionPoints() {
    return collectedAnime.reduce((total, anime) => total + getAnimeScore(anime), 0);
}

function getAnimeScore(anime) {
    const score = Number(anime.averageScore ?? anime.score ?? 0);
    return Number.isFinite(score) ? score : 0;
}

function addAnimePrice(anime) {
    return {
        ...anime,
        price: getAnimePrice(anime) || Math.floor(Math.random() * 10) + 1
    };
}

function getAnimePrice(anime) {
    const price = Number(anime.price ?? 0);
    return Number.isFinite(price) ? price : 0;
}

function calculateFuelCost(distanceKm) {
    return Math.max(1, Math.ceil(distanceKm * FUEL_PER_KM));
}

function spendFuelForDistance(distanceKm) {
    if (gameState.gameOver) {
        return false;
    }

    const fuelCost = calculateFuelCost(distanceKm);
    gameState.fuel -= fuelCost;
    saveStoredGameState();
    renderGameStatus();

    if (gameState.fuel <= 0) {
        endGame('Fuel ran out');
        return false;
    }

    return true;
}

function renderGameStatus() {
    const playerName = document.getElementById('player-name-val');
    const fuel = document.getElementById('fuel-val');
    const money = document.getElementById('money-val');

    if (playerName) {
        playerName.textContent = gameState.playerName || '-';
    }

    if (fuel) {
        fuel.textContent = `${Math.max(0, Math.ceil(gameState.fuel))} L`;
    }

    if (money) {
        money.textContent = `${Math.max(0, gameState.money)} €`;
    }
}

function endGame(reason) {
    gameState.gameOver = true;
    gameState.gameOverReason = reason;
    saveFinishedRunToLeaderboard();
    saveStoredGameState();
    renderGameStatus();
    renderAnimeInventory();
    renderLeaderboard();
    alert(`Game over: ${reason}`);
}

function saveFinishedRunToLeaderboard() {
    if (gameState.leaderboardSaved) {
        return;
    }

    const entry = {
        playerName: gameState.playerName || 'Unknown',
        score: calculateCollectionPoints(),
        collectedCount: collectedAnime.length,
        endedAt: new Date().toISOString()
    };

    leaderboard.push(entry);
    leaderboard.sort((a, b) => b.score - a.score);
    leaderboard = leaderboard.slice(0, LEADERBOARD_LIMIT);
    gameState.leaderboardSaved = true;
    saveStoredLeaderboard();
    saveStoredGameState();
}

function renderLeaderboard() {
    const body = document.getElementById('leaderboard-body');
    const empty = document.getElementById('leaderboard-empty');
    const newRunButton = document.getElementById('new-run-btn');

    if (!body || !empty) {
        return;
    }

    body.innerHTML = '';
    empty.hidden = leaderboard.length > 0;

    if (newRunButton) {
        newRunButton.hidden = !gameState.gameOver;
    }

    leaderboard.forEach((entry, index) => {
        const row = document.createElement('tr');
        const rankCell = document.createElement('td');
        const nameCell = document.createElement('td');
        const scoreCell = document.createElement('td');

        rankCell.textContent = String(index + 1);
        nameCell.textContent = entry.playerName;
        scoreCell.textContent = String(entry.score);

        row.appendChild(rankCell);
        row.appendChild(nameCell);
        row.appendChild(scoreCell);
        body.appendChild(row);
    });
}

function setupNewRunButton() {
    const button = document.getElementById('new-run-btn');

    if (!button || button.dataset.ready === 'true') {
        return;
    }

    button.dataset.ready = 'true';
    button.addEventListener('click', startNewRun);
}

function startNewRun() {
    gameState = {
        fuel: INITIAL_FUEL,
        money: INITIAL_MONEY,
        playerName: '',
        gameOver: false,
        gameOverReason: null,
        leaderboardSaved: false
    };

    inventoryAnime = [];
    collectedAnime = [];
    saveStoredGameState();
    saveStoredCollection();
    renderGameStatus();
    renderCollection();
    setupPlayerNameModal(true);
    loadRandomAnimeInventory();
}

function setupPlayerNameModal(force = false) {
    const modal = document.getElementById('playerNameModal');
    const input = document.getElementById('player-name-input');
    const confirm = document.getElementById('player-name-confirm');

    if (!modal || !input || !confirm || (!force && gameState.playerName)) {
        return;
    }

    modal.classList.add('active');
    input.value = '';
    input.focus();

    const saveName = () => {
        const name = input.value.trim();

        if (!name) {
            input.focus();
            return;
        }

        gameState.playerName = name;
        saveStoredGameState();
        renderGameStatus();
        modal.classList.remove('active');
    };

    confirm.onclick = saveName;
    input.onkeydown = (event) => {
        if (event.key === 'Enter') {
            saveName();
        }
    };
}

function loadStoredCollection() {
    try {
        return JSON.parse(localStorage.getItem(COLLECTION_STORAGE_KEY)) || [];
    } catch (error) {
        console.error('Error loading anime collection:', error);
        return [];
    }
}

function saveStoredCollection() {
    try {
        localStorage.setItem(COLLECTION_STORAGE_KEY, JSON.stringify(collectedAnime));
    } catch (error) {
        console.error('Error saving anime collection:', error);
    }
}

function loadStoredGameState() {
    try {
        return {
            fuel: INITIAL_FUEL,
            money: INITIAL_MONEY,
            playerName: '',
            gameOver: false,
            gameOverReason: null,
            leaderboardSaved: false,
            ...(JSON.parse(localStorage.getItem(GAME_STATE_STORAGE_KEY)) || {})
        };
    } catch (error) {
        console.error('Error loading game state:', error);
        return {
            fuel: INITIAL_FUEL,
            money: INITIAL_MONEY,
            playerName: '',
            gameOver: false,
            gameOverReason: null,
            leaderboardSaved: false
        };
    }
}

function saveStoredGameState() {
    try {
        localStorage.setItem(GAME_STATE_STORAGE_KEY, JSON.stringify(gameState));
    } catch (error) {
        console.error('Error saving game state:', error);
    }
}

function loadStoredLeaderboard() {
    try {
        const storedLeaderboard = JSON.parse(localStorage.getItem(LEADERBOARD_STORAGE_KEY)) || [];

        return storedLeaderboard
            .filter((entry) => entry && typeof entry.playerName === 'string')
            .sort((a, b) => Number(b.score || 0) - Number(a.score || 0))
            .slice(0, LEADERBOARD_LIMIT);
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        return [];
    }
}

function saveStoredLeaderboard() {
    try {
        localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(leaderboard));
    } catch (error) {
        console.error('Error saving leaderboard:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadRandomAnimeInventory);
