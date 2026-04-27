from flask import Blueprint

cart_bp = Blueprint('cart', __name__)

@cart_bp.route("/cart")
def cart():
    return "cart endpoint"