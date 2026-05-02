from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from api.database.db import engine
from api.database.models import Game, Airport

bp = Blueprint('game', __name__)

Session = sessionmaker(bind=engine)


@bp.route('/create', methods=['POST'])
def create_game():
    """
    Create a new game session.
    Expects JSON with screen_name and optional starting location.
    """
    try:
        data = request.get_json()
        
        if not data or 'screen_name' not in data:
            return jsonify({'error': 'Missing screen_name'}), 400
        
        screen_name = data['screen_name'].strip()
        
        if not screen_name:
            return jsonify({'error': 'screen_name cannot be empty'}), 400
        
        location = data.get('location')
        
        session = Session()
        try:
            # If no location provided, use the first available airport
            if not location:
                airport = session.query(Airport).first()
                if not airport:
                    return jsonify({'error': 'No airports available'}), 500
                location = airport.ident
            else:
                # Verify the airport exists
                airport = session.query(Airport).filter_by(ident=location).first()
                if not airport:
                    return jsonify({'error': 'Invalid airport location'}), 400
            
            new_game = Game(
                screen_name=screen_name,
                location=location,
                points=0,
                money=0
            )
            
            session.add(new_game)
            session.commit()
            
            return jsonify({
                'success': True,
                'game_id': new_game.id,
                'screen_name': new_game.screen_name,
                'location': new_game.location,
                'points': new_game.points,
                'money': new_game.money
            }), 201
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """
    Get game info including current location details.
    Returns game data with full airport information.
    """
    try:
        session = Session()
        try:
            # Fetch the game
            game = session.query(Game).filter_by(id=game_id).first()
            
            if not game:
                return jsonify({'error': 'Game not found'}), 404
            
            # Fetch the airport data for current location
            airport = session.query(Airport).filter_by(ident=game.location).first()
            
            if not airport:
                return jsonify({'error': 'Location airport not found'}), 500
            
            # Build response with game and airport info
            return jsonify({
                'success': True,
                'game': {
                    'id': game.id,
                    'screen_name': game.screen_name,
                    'points': game.points,
                    'money': game.money,
                    'location': game.location
                },
                'current_airport': {
                    'ident': airport.ident,
                    'name': airport.name,
                    'type': airport.type,
                    'municipality': airport.municipality,
                    'latitude_deg': airport.latitude_deg,
                    'longitude_deg': airport.longitude_deg,
                    'elevation_ft': airport.elevation_ft,
                    'continent': airport.continent,
                    'iso_country': airport.iso_country,
                    'iso_region': airport.iso_region
                }
            }), 200
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:game_id>/location', methods=['PUT'])
def update_location(game_id):
    """
    Update the player's current location by airport identifier.
    Changes the location foreign key and fetches the new airport data.
    """
    try:
        data = request.get_json()
        
        if not data or 'location' not in data:
            return jsonify({'error': 'Missing location (airport ident)'}), 400
        
        location = data['location'].strip().upper()
        
        if not location:
            return jsonify({'error': 'Location cannot be empty'}), 400
        
        session = Session()
        try:
            # Fetch the game
            game = session.query(Game).filter_by(id=game_id).first()
            
            if not game:
                return jsonify({'error': 'Game not found'}), 404
            
            # Verify the airport exists
            airport = session.query(Airport).filter_by(ident=location).first()
            
            if not airport:
                return jsonify({'error': 'Invalid airport location'}), 400
            
            # Update the location
            old_location = game.location
            game.location = location
            session.commit()
            
            return jsonify({
                'success': True,
                'game_id': game.id,
                'old_location': old_location,
                'new_location': game.location,
                'current_airport': {
                    'ident': airport.ident,
                    'name': airport.name,
                    'type': airport.type,
                    'municipality': airport.municipality,
                    'latitude_deg': airport.latitude_deg,
                    'longitude_deg': airport.longitude_deg,
                    'elevation_ft': airport.elevation_ft,
                    'continent': airport.continent,
                    'iso_country': airport.iso_country,
                    'iso_region': airport.iso_region
                }
            }), 200
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:game_id>/travel', methods=['POST'])
def travel(game_id):
    """
    Travel from current location to a destination airport.
    Validates destination exists and updates the game's location.
    Can optionally apply resource costs (fuel/time deduction).
    """
    try:
        data = request.get_json()
        
        if not data or 'destination' not in data:
            return jsonify({'error': 'Missing destination (airport ident)'}), 400
        
        destination = data['destination'].strip().upper()
        
        if not destination:
            return jsonify({'error': 'Destination cannot be empty'}), 400
        
        session = Session()
        try:
            # Fetch the game
            game = session.query(Game).filter_by(id=game_id).first()
            
            if not game:
                return jsonify({'error': 'Game not found'}), 404
            
            # Get current location airport
            current_airport = session.query(Airport).filter_by(ident=game.location).first()
            
            if not current_airport:
                return jsonify({'error': 'Current location airport not found'}), 500
            
            # Verify destination airport exists
            destination_airport = session.query(Airport).filter_by(ident=destination).first()
            
            if not destination_airport:
                return jsonify({'error': 'Destination airport not found'}), 400
            
            # Check if already at destination
            if game.location == destination:
                return jsonify({'error': 'Already at this location'}), 400
            
            # Calculate distance (Haversine formula for great circle distance)
            import math
            
            lat1 = math.radians(current_airport.latitude_deg)
            lon1 = math.radians(current_airport.longitude_deg)
            lat2 = math.radians(destination_airport.latitude_deg)
            lon2 = math.radians(destination_airport.longitude_deg)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            earth_radius_km = 6371
            distance_km = earth_radius_km * c
            
            # Update location
            game.location = destination
            session.commit()
            
            return jsonify({
                'success': True,
                'game_id': game.id,
                'traveled_from': current_airport.ident,
                'traveled_to': destination_airport.ident,
                'distance_km': round(distance_km, 2),
                'previous_airport': {
                    'ident': current_airport.ident,
                    'name': current_airport.name,
                    'municipality': current_airport.municipality
                },
                'current_airport': {
                    'ident': destination_airport.ident,
                    'name': destination_airport.name,
                    'type': destination_airport.type,
                    'municipality': destination_airport.municipality,
                    'latitude_deg': destination_airport.latitude_deg,
                    'longitude_deg': destination_airport.longitude_deg,
                    'elevation_ft': destination_airport.elevation_ft,
                    'continent': destination_airport.continent,
                    'iso_country': destination_airport.iso_country,
                    'iso_region': destination_airport.iso_region
                }
            }), 200
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
