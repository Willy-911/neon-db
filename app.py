from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

conn = psycopg2.connect(os.environ.get("DATABASE_URL"))

@app.route("/")
def home():
    return "API is running"

@app.route("/users")
def users():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    data = cur.fetchall()
    return jsonify(data)