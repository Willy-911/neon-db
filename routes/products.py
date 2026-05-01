import json

from flask import Blueprint, Response, request

from db import get_connection

products_bp = Blueprint("products", __name__)


def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        status=status,
        content_type="application/json; charset=utf-8",
    )


@products_bp.route("/products", methods=["GET"])
def get_products():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY id DESC;")

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(columns, row)) for row in rows]

        return json_response(result)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@products_bp.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = %s;", (id,))
        row = cur.fetchone()

        if not row:
            return {"error": "Product not found"}, 404

        columns = [desc[0] for desc in cur.description]
        return json_response(dict(zip(columns, row)))
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@products_bp.route("/products", methods=["POST"])
def add_product():
    data = request.json
    if not data:
        return {"error": "Request body is required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products
            (
                title_ar,
                category,
                price,
                location_ar,
                description_ar,
                main_image,
                extra_images,
                is_sold,
                owner_uid
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            data.get("title_ar"),
            data.get("category"),
            data.get("price"),
            data.get("location_ar"),
            data.get("description_ar"),
            data.get("main_image"),
            data.get("extra_images", "[]"),
            data.get("is_sold", False),
            data.get("owner_uid"),
        ))

        new_product = cur.fetchone()
        conn.commit()

        columns = [desc[0] for desc in cur.description]
        return json_response(dict(zip(columns, new_product)), 201)
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@products_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.json
    if not data:
        return {"error": "Request body is required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE products
            SET
                title_ar=%s,
                category=%s,
                price=%s,
                location_ar=%s,
                description_ar=%s,
                main_image=%s,
                extra_images=%s,
                is_sold=%s
            WHERE id=%s AND owner_uid=%s
            RETURNING *;
        """, (
            data.get("title_ar"),
            data.get("category"),
            data.get("price"),
            data.get("location_ar"),
            data.get("description_ar"),
            data.get("main_image"),
            data.get("extra_images", "[]"),
            data.get("is_sold", False),
            id,
            data.get("owner_uid"),
        ))

        updated = cur.fetchone()
        conn.commit()

        if not updated:
            return {"error": "Product not found"}, 404

        columns = [desc[0] for desc in cur.description]
        return json_response(dict(zip(columns, updated)))
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@products_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    owner_uid = request.args.get("owner_uid")
    if not owner_uid:
        return {"error": "owner_uid is required"}, 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM favorites WHERE product_id=%s;", (id,))
        cur.execute("DELETE FROM cart WHERE product_id=%s;", (id,))
        cur.execute(
            "DELETE FROM products WHERE id=%s AND owner_uid=%s RETURNING *;",
            (id, owner_uid),
        )
        deleted = cur.fetchone()
        conn.commit()

        if not deleted:
            return {"error": "Product not found"}, 404

        return {"message": "Product deleted successfully"}
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
