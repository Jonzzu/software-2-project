from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from api.database.db import engine
from api.database.models import Collection, Series, Game

bp = Blueprint('collection', __name__)

Session = sessionmaker(bind=engine)


@bp.route('/create', methods=['POST'])
def create_collection():
    """
    Create a new collection for a game instance.
    Expects JSON with screen_name and optional name/description.
    """
    try:
        data = request.get_json()
        
        if not data or 'screen_name' not in data:
            return jsonify({'error': 'Missing screen_name'}), 400
        
        screen_name = data['screen_name'].strip()
        
        if not screen_name:
            return jsonify({'error': 'screen_name cannot be empty'}), 400
        
        # Verify that the game instance exists
        session = Session()
        try:
            game = session.query(Game).filter_by(screen_name=screen_name).first()
            
            if not game:
                return jsonify({'error': 'Game instance not found for this screen_name'}), 404
            
            collection_name = data.get('name', f'{screen_name}\'s Collection').strip()
            description = data.get('description', '').strip() or None
            
            new_collection = Collection(
                name=collection_name,
                screen_name=screen_name,
                description=description
            )
            
            session.add(new_collection)
            session.commit()
            
            return jsonify({
                'success': True,
                'collection_id': new_collection.id,
                'name': new_collection.name,
                'screen_name': new_collection.screen_name,
                'description': new_collection.description,
                'series_count': 0
            }), 201
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/add-series', methods=['POST'])
def add_series_to_collection():
    """
    Add a series to a collection.
    Expects JSON with collection_id and series_id (or create new series data).
    """
    try:
        data = request.get_json()
        
        if not data or 'collection_id' not in data:
            return jsonify({'error': 'Missing collection_id'}), 400
        
        collection_id = data['collection_id']
        series_id = data.get('series_id')
        
        session = Session()
        try:
            # Fetch the collection
            collection = session.query(Collection).filter_by(id=collection_id).first()
            
            if not collection:
                return jsonify({'error': 'Collection not found'}), 404
            
            # If series_id provided, use existing series
            if series_id:
                series = session.query(Series).filter_by(id=series_id).first()
                
                if not series:
                    return jsonify({'error': 'Series not found'}), 404
                
                # Check if series is already in collection
                if series in collection.series:
                    return jsonify({'error': 'Series already in collection'}), 400
                
                collection.series.append(series)
            
            # Otherwise, create new series and add it
            else:
                if 'name' not in data:
                    return jsonify({'error': 'Missing series name'}), 400
                
                series_name = data['name'].strip()
                
                if not series_name:
                    return jsonify({'error': 'Series name cannot be empty'}), 400
                
                new_series = Series(
                    name=series_name,
                    anilist_id=data.get('anilist_id'),
                    rating=float(data.get('rating', 0.0)),
                    description=data.get('description'),
                    cover_image_url=data.get('cover_image_url')
                )
                
                session.add(new_series)
                session.flush()  # Get the ID before committing
                
                collection.series.append(new_series)
                series = new_series
            
            session.commit()
            
            return jsonify({
                'success': True,
                'collection_id': collection.id,
                'series_id': series.id,
                'series_name': series.name,
                'rating': series.rating,
                'series_count': len(collection.series)
            }), 201
        
        finally:
            session.close()
    
    except ValueError:
        return jsonify({'error': 'Invalid rating value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/game/<screen_name>', methods=['GET'])
def get_game_collections(screen_name):
    """
    Fetch all collections for a specific game instance (by screen_name).
    Returns a list of all collections with series counts.
    """
    try:
        screen_name = screen_name.strip()
        
        if not screen_name:
            return jsonify({'error': 'screen_name cannot be empty'}), 400
        
        session = Session()
        try:
            # Verify game exists
            game = session.query(Game).filter_by(screen_name=screen_name).first()
            
            if not game:
                return jsonify({'error': 'Game instance not found'}), 404
            
            # Fetch all collections for this screen_name
            collections = session.query(Collection).filter_by(screen_name=screen_name).all()
            
            collections_data = [
                {
                    'id': c.id,
                    'name': c.name,
                    'screen_name': c.screen_name,
                    'description': c.description,
                    'series_count': len(c.series),
                    'total_rating': sum(s.rating for s in c.series) if c.series else 0
                }
                for c in collections
            ]
            
            return jsonify({
                'success': True,
                'screen_name': screen_name,
                'collections': collections_data
            }), 200
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:collection_id>/series', methods=['GET'])
def get_collection_series(collection_id):
    """
    Fetch all series in a specific collection.
    Returns detailed information about each series.
    """
    try:
        session = Session()
        try:
            # Fetch the collection
            collection = session.query(Collection).filter_by(id=collection_id).first()
            
            if not collection:
                return jsonify({'error': 'Collection not found'}), 404
            
            # Build series data
            series_data = [
                {
                    'id': s.id,
                    'name': s.name,
                    'anilist_id': s.anilist_id,
                    'rating': s.rating,
                    'description': s.description,
                    'cover_image_url': s.cover_image_url
                }
                for s in collection.series
            ]
            
            return jsonify({
                'success': True,
                'collection': {
                    'id': collection.id,
                    'name': collection.name,
                    'screen_name': collection.screen_name,
                    'description': collection.description
                },
                'series': series_data,
                'series_count': len(series_data),
                'total_rating': sum(s['rating'] for s in series_data) if series_data else 0
            }), 200
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500