from flask import Blueprint, request, Response
from db import get_connection
import json

favorites_bp = Blueprint('favorites', __name__)

# ✅ Get Favorites
@favorites_bp.route("/favorites/<user_id>", methods=["GET"])
def get_favorites(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT f.id, f.product_id, p.title_ar, p.price, p.main_image
        FROM favorites f
        JOIN products p ON f.product_id = p.id
        WHERE f.user_id = %s;
    """, (user_id,))

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return Response(json.dumps(result, ensure_ascii=False), content_type="application/json")


# ✅ Toggle Favorite
@favorites_bp.route("/favorites", methods=["POST"])
def toggle_favorite():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    # check لو موجود
    cur.execute("""
        SELECT * FROM favorites
        WHERE user_id=%s AND product_id=%s;
    """, (data["user_id"], data["product_id"]))

    exists = cur.fetchone()

    if exists:
        cur.execute("""
            DELETE FROM favorites
            WHERE user_id=%s AND product_id=%s;
        """, (data["user_id"], data["product_id"]))
        message = "Removed from favorites"
    else:
        cur.execute("""
            INSERT INTO favorites (user_id, product_id)
            VALUES (%s, %s);
        """, (data["user_id"], data["product_id"]))
        message = "Added to favorites"

    conn.commit()

    cur.close()
    conn.close()

    return {"message": message}
