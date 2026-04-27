from flask import Blueprint, Response
from db import get_connection
import json

users_bp = Blueprint('users', __name__)

@users_bp.route("/users")
def get_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users;")

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return Response(
        json.dumps(result, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8"
    )