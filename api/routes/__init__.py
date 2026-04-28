from flask import Blueprint
from .map import bp as map_bp

# Create main API blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

# Register sub-blueprints with their own prefixes
bp.register_blueprint(map_bp, url_prefix='/map')
