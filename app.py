from flask import Flask, Response
import psycopg2
import os
import json

app = Flask(__name__)

conn = psycopg2.connect(
    os.environ.get("DATABASE_URL"),
    sslmode="require"
)

@app.route("/")
def home():
    return "API is running"

@app.route("/users")
def users():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append(dict(zip(columns, row)))

    return Response(
        json.dumps(result, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8"
    )
