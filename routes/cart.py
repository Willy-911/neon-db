from flask import Blueprint, request, Response
from db import get_connection
import json

cart_bp = Blueprint('cart', __name__)

# ✅ Get User Cart
@cart_bp.route("/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.product_id, p.title_ar, p.price, p.main_image
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s;
    """, (user_id,))

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return Response(json.dumps(result, ensure_ascii=False), content_type="application/json")


# ✅ Add To Cart
@cart_bp.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cart (user_id, product_id)
        VALUES (%s, %s)
        RETURNING *;
    """, (data["user_id"], data["product_id"]))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Added to cart"}, 201


# ✅ Remove From Cart
@cart_bp.route("/cart", methods=["DELETE"])
def remove_from_cart():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM cart
        WHERE user_id=%s AND product_id=%s;
    """, (data["user_id"], data["product_id"]))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Removed from cart"}
