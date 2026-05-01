import json

from flask import Blueprint, Response, request
from psycopg2 import sql

from db import get_connection

cart_bp = Blueprint("cart", __name__)


def get_cart_user_column(cur):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'cart';
    """)

    columns = {row[0] for row in cur.fetchall()}
    for column in ("user_id", "firebase_uid", "user_uid", "uid", "owner_uid"):
        if column in columns:
            return column

    raise Exception(
        "No user column found in cart table. Expected one of: "
        "user_id, firebase_uid, user_uid, uid, owner_uid"
    )


@cart_bp.route("/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        user_column = get_cart_user_column(cur)

        cur.execute(
            sql.SQL("""
                SELECT
                    c.id AS cart_id,
                    c.product_id,
                    p.title_ar,
                    p.category,
                    p.price,
                    p.location_ar,
                    p.description_ar,
                    p.main_image,
                    p.extra_images,
                    p.is_sold
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.{user_column} = %s;
            """).format(user_column=sql.Identifier(user_column)),
            (user_id,),
        )

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(columns, row)) for row in rows]

        return Response(
            json.dumps(result, ensure_ascii=False, default=str),
            content_type="application/json; charset=utf-8",
        )
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@cart_bp.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.json
    if not data or "user_id" not in data or "product_id" not in data:
        return {"error": "user_id and product_id are required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        user_column = get_cart_user_column(cur)

        cur.execute(
            sql.SQL("""
                SELECT *
                FROM cart
                WHERE {user_column} = %s AND product_id = %s;
            """).format(user_column=sql.Identifier(user_column)),
            (data["user_id"], data["product_id"]),
        )

        if cur.fetchone():
            return {"message": "Already in cart"}

        cur.execute(
            sql.SQL("""
                INSERT INTO cart ({user_column}, product_id)
                VALUES (%s, %s);
            """).format(user_column=sql.Identifier(user_column)),
            (data["user_id"], data["product_id"]),
        )

        conn.commit()
        return {"message": "Added to cart"}, 201
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@cart_bp.route("/cart", methods=["DELETE"])
def remove_from_cart():
    data = request.json
    if not data or "user_id" not in data or "product_id" not in data:
        return {"error": "user_id and product_id are required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        user_column = get_cart_user_column(cur)

        cur.execute(
            sql.SQL("""
                DELETE FROM cart
                WHERE {user_column} = %s AND product_id = %s;
            """).format(user_column=sql.Identifier(user_column)),
            (data["user_id"], data["product_id"]),
        )

        conn.commit()
        return {"message": "Removed from cart"}
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
