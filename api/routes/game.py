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
