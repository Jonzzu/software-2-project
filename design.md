# 📘 Design Document: Anime Flight Explorer

## Project Overview

**Game Title:** Anime Flight Explorer  
**Description:** A text-based roguelike adventure where players traverse a world map as a pilot, collecting anime series and accumulating points based on their ratings.

**Language:** Python 3.14 (Backend: Flask, Frontend: Vanilla JS)  
**Target:** MVP with localStorage persistence

---

## Game Mechanics

### Core Loop
1. **Map Navigation** → Select destination → Travel (costs fuel/time)
2. **Series Encounter** → View 1-n anime from AniList API → Select or skip
3. **Scoring** → Collect points based on series ratings
4. **Resource Management** → Fuel/Time deplete with actions
5. **Game Over** → Resources depleted OR target points reached

### Scoring System
- **Points Source:** Average rating from collected anime series
- **Calculation:** `points += average_rating * series_count` or simple sum
- **Display:** Real-time score counter visible at all times

### Resource System
- **Fuel/Time Pool:** Starting value (e.g., 100 units)
- **Travel Cost:** Depends on destination distance (5-20 units)
- **Action Cost:** Selecting/skipping series (1 unit)
- **Win Condition:** Reach target points (e.g., 500) before depleting resources

---

## MVP Feature Breakdown

| Feature | Status | Description |
|---------|--------|-------------|
| Map View | Required | Grid/list of destinations with distance info |
| Destination Navigation | Required | Travel between airports, consume fuel |
| AniList Integration | Required | Fetch anime data with error handling & retry |
| Series Selection UI | Required | Display series with image, name, rating |
| Point System | Required | Calculate & display score |
| Resource Tracking | Required | Show fuel/time remaining |
| Collection View | Required | Display collected series & stats |
| Game Over Screen | Required | Show final score & restart option |
| Data Persistence | Required | Save game state (localStorage or SQLite) |
| Error Handling | Required | Graceful API failures with user feedback |

---

## Out of Scope (v1)
- ❌ Skill trees or character progression
- ❌ Economy/trading system
- ❌ Leaderboards
- ❌ User accounts & cloud sync
- ❌ Multiplayer features

---

## Architecture Overview

### Backend (Flask)
- REST API for game state management
- AniList API proxy with caching & error handling
- Game logic: scoring, resource management, win/lose conditions
- SQLite for persistent storage (optional for MVP)

### Frontend (Vanilla JS + HTML/CSS)
- Single-page application
- Responsive map view
- Modal dialogs for series selection
- Real-time score & resource display
- localStorage fallback for offline play

### Data Flow
```
Client (JS) ↔ Backend API (Flask) ↔ Database (SQLite) + AniList API
```

---

## Folder Structure
```
software-2-project/
├── api/                          # Backend Flask application
│   ├── __init__.py
│   ├── main.py                   # Flask app entry point
│   ├── config.py                 # Configuration (API keys, constants)
│   │
│   ├── database/                 # Data layer
│   │   ├── __init__.py
│   │   ├── db.py                 # Database initialization & session
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── __init__.py       # Package export
│   │   │   ├── base.py           # Base declarative class
│   │   │   ├── game.py           # Game session model
│   │   │   ├── airport.py        # Airport/destination model
│   │   │   ├── country.py        # Country/region model
│   │   │   └── goal.py           # (Optional) Goal/achievement model
│   │   └── dump/                 # Database backups/migrations
│   │
│   ├── routes/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── game.py               # Game state endpoints
│   │   ├── map.py                # Map/destination endpoints
│   │   ├── series.py             # Series selection endpoints
│   │   └── anilist/              # AniList integration
│   │       ├── __init__.py
│   │       └── client.py         # AniList API client
│   │
│   ├── services/                 # Business logic (NEW)
│   │   ├── __init__.py
│   │   ├── game_service.py       # Game state & scoring logic
│   │   ├── resource_service.py   # Fuel/time management
│   │   └── anilist_service.py    # API calls & caching
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── import_db.py          # Database seeding
│   │   ├── errors.py             # Custom exceptions (NEW)
│   │   └── validators.py         # Input validation (NEW)
│   │
│   └── sqlite/                   # SQLite database file
│       └── game.db
│
├── client/                       # Frontend application
│   ├── index.html                # Main HTML
│   ├── js/                       # JavaScript (NEW)
│   │   ├── main.js               # App initialization
│   │   ├── api.js                # Backend API client
│   │   ├── game.js               # Game state & logic
│   │   ├── ui.js                 # UI rendering
│   │   └── storage.js            # localStorage management
│   ├── styles/                   # CSS
│   │   ├── main.css              # Global styles
│   │   ├── map.css               # Map view styles
│   │   └── modal.css             # Dialog styles
│   └── img/                      # Images & assets
│       ├── icons/                # UI icons
│       └── backgrounds/          # BG images
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # Project documentation
```

---

## Key Design Decisions

### 1. **API Architecture**
- RESTful endpoints for game operations
- Stateless backend (session stored in DB)
- CORS enabled for local dev

### 2. **Error Handling**
- AniList API failures → User-friendly message + retry button
- Invalid moves → Clear validation errors
- Network errors → Offline fallback (cached data)

### 3. **Data Persistence**
- **Primary:** SQLite (persistent, no server needed)
- **Fallback:** localStorage (client-side, game state only)
- **Auto-save:** Every action triggers a save

### 4. **AniList Integration**
- GraphQL queries for anime search
- Caching layer to reduce API calls
- Graceful degradation if API unavailable

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Flask 2.x | Web framework |
| Database | SQLAlchemy + SQLite | ORM & persistence |
| API Client | Requests | HTTP calls to AniList |
| Frontend | HTML5 + Vanilla JS | UI & interactions |
| Styling | CSS3 | Responsive design |
| State | localStorage | Client-side cache |

---

## Development Phases

### Phase 1: Backend Foundation
- [ ] Database models & migrations
- [ ] Flask app structure & routes
- [ ] AniList API client
- [ ] Game logic (scoring, resources)

### Phase 2: Frontend UI
- [ ] HTML structure
- [ ] Map view & navigation
- [ ] Series selection modal
- [ ] Score/resource display

### Phase 3: Integration
- [ ] API client in JavaScript
- [ ] Game state synchronization
- [ ] Save/load functionality
- [ ] Error handling & UX polish

### Phase 4: Polish & Testing
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] UI/UX refinement
- [ ] Documentation

---

## Future Enhancements (Post-MVP)

- 🎮 Difficulty levels & difficulty multipliers
- 🌍 More destinations & world events
- 💾 Cloud save with user accounts
- 📊 Statistics tracking & achievements
- 🎨 Anime artwork gallery integration
- ⚙️ Settings & gameplay customization