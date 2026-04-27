from flask import Blueprint

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route("/favorites")
def favorites():
    return "favorites endpoint"