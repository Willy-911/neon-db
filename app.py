from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# الاتصال بالداتابيز (Neon)
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

    return jsonify(result)
