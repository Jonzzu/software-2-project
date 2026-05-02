from flask import Blueprint, jsonify
from .get_random import get_random_anime

bp = Blueprint('anilist', __name__, url_prefix='/api/anilist')


@bp.route('/random-series', methods=['GET'])
def random_series():
    """
    Get 3 random anime series from AniList.
    Returns a list of 3 series with id, title, score, description, and image.
    """
    try:
        anime_list = get_random_anime(n=3)
        
        if not anime_list:
            return jsonify({'error': 'Failed to fetch random series'}), 500
        
        return jsonify({
            'success': True,
            'series': anime_list
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500