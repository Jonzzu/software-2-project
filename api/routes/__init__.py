from flask import Blueprint
from .map import bp as map_bp
from .game import bp as game_bp
from .anilist import bp as anilist_bp

# Create main API blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

# Register sub-blueprints with their own prefixes
bp.register_blueprint(map_bp, url_prefix='/map')
bp.register_blueprint(game_bp, url_prefix='/game')
bp.register_blueprint(anilist_bp, url_prefix='/anilist')
