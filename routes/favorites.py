import json

from flask import Blueprint, Response, request
from psycopg2 import sql

from db import get_connection

favorites_bp = Blueprint("favorites", __name__)


def get_favorites_user_column(cur):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'favorites';
    """)

    columns = {row[0] for row in cur.fetchall()}
    for column in ("user_id", "firebase_uid", "user_uid", "uid", "owner_uid"):
        if column in columns:
            return column

    raise Exception(
        "No user column found in favorites table. Expected one of: "
        "user_id, firebase_uid, user_uid, uid, owner_uid"
    )


@favorites_bp.route("/favorites/<user_id>", methods=["GET"])
def get_favorites(user_id):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        user_column = get_favorites_user_column(cur)

        cur.execute(
            sql.SQL("""
                SELECT f.id, f.product_id, p.title_ar, p.price, p.main_image
                FROM favorites f
                JOIN products p ON f.product_id = p.id
                WHERE f.{user_column} = %s;
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


@favorites_bp.route("/favorites", methods=["POST"])
def toggle_favorite():
    data = request.json
    if not data or "user_id" not in data or "product_id" not in data:
        return {"error": "user_id and product_id are required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        user_column = get_favorites_user_column(cur)

        cur.execute(
            sql.SQL("""
                SELECT *
                FROM favorites
                WHERE {user_column} = %s AND product_id = %s;
            """).format(user_column=sql.Identifier(user_column)),
            (data["user_id"], data["product_id"]),
        )

        exists = cur.fetchone()

        if exists:
            cur.execute(
                sql.SQL("""
                    DELETE FROM favorites
                    WHERE {user_column} = %s AND product_id = %s;
                """).format(user_column=sql.Identifier(user_column)),
                (data["user_id"], data["product_id"]),
            )
            message = "Removed from favorites"
        else:
            cur.execute(
                sql.SQL("""
                    INSERT INTO favorites ({user_column}, product_id)
                    VALUES (%s, %s);
                """).format(user_column=sql.Identifier(user_column)),
                (data["user_id"], data["product_id"]),
            )
            message = "Added to favorites"

        conn.commit()
        return {"message": message}
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
