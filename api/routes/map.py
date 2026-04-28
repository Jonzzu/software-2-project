from typing import List, Dict
from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from api.database.db import engine
from api.database.models import Airport

# Create blueprint without url_prefix (parent handles it)
bp = Blueprint('map', __name__)

# Create session factory
Session = sessionmaker(bind=engine)


@bp.route('/airports', methods=['GET'])
def get_airports_route():
    """
    Fetch large airports with name, ICAO code, latitude, and longitude.
    
    Returns:
        JSON list of large airports with their coordinates
    """
    session = Session()
    try:
        # Query only large airports from database
        airports = session.query(Airport).filter(Airport.type == "large_airport").all()
        
        # Extract required fields
        airports_data = [
            {
                "name": airport.name,
                "icao": airport.ident,
                "latitude": airport.latitude_deg,
                "longitude": airport.longitude_deg
            }
            for airport in airports
        ]
        
        return jsonify({
            "success": True,
            "count": len(airports_data),
            "airports": airports_data
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
    finally:
        session.close()


def get_airports() -> List[Dict]:
    """
    Helper function to get large airports (non-route version).
    Useful for internal game logic.
    
    Returns:
        List of large airport dictionaries
    """
    session = Session()
    try:
        airports = session.query(Airport).filter(Airport.type == "large_airport").all()
        
        return [
            {
                "name": airport.name,
                "icao": airport.ident,
                "latitude": airport.latitude_deg,
                "longitude": airport.longitude_deg
            }
            for airport in airports
        ]
    
    finally:
        session.close()

