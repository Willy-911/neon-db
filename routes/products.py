from flask import Blueprint, Response, request
from db import get_connection
import json

products_bp = Blueprint('products', __name__)

# ✅ 1. Get All Products
@products_bp.route("/products", methods=["GET"])
def get_products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products;")

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return Response(
        json.dumps(result, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8"
    )

# ✅ 2. Get Product by ID
@products_bp.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products WHERE id = %s;", (id,))
    row = cur.fetchone()

    if not row:
        return {"error": "Product not found"}, 404

    columns = [desc[0] for desc in cur.description]
    result = dict(zip(columns, row))

    cur.close()
    conn.close()

    return result

# ✅ 3. Add Product
@products_bp.route("/products", methods=["POST"])
def add_product():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO products 
    (title_ar, category, price, location_ar, description_ar, main_image, extra_images, is_sold, owner_uid)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING *;
""", (
    data.get("title_ar"),
    data.get("category"),
    data.get("price"),
    data.get("location_ar"),
    data.get("description_ar"),
    data.get("main_image"),
    data.get("extra_images"),
    data.get("is_sold"),
    data.get("owner_uid")
))

    new_product = cur.fetchone()
    conn.commit()

    columns = [desc[0] for desc in cur.description]
    result = dict(zip(columns, new_product))

    cur.close()
    conn.close()

    return result, 201

# ✅ 4. Update Product
@products_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE products
        SET name=%s, price=%s, location=%s, category=%s, image=%s
        WHERE id=%s
        RETURNING *;
    """, (
        data.get("name"),
        data.get("price"),
        data.get("location"),
        data.get("category"),
        data.get("image"),
        id
    ))

    updated = cur.fetchone()
    conn.commit()

    if not updated:
        return {"error": "Product not found"}, 404

    columns = [desc[0] for desc in cur.description]
    result = dict(zip(columns, updated))

    cur.close()
    conn.close()

    return result

# ✅ 5. Delete Product
@products_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM products WHERE id=%s RETURNING *;", (id,))
    deleted = cur.fetchone()
    conn.commit()

    if not deleted:
        return {"error": "Product not found"}, 404

    cur.close()
    conn.close()

    return {"message": "Product deleted successfully"}
