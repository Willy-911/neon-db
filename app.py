from flask import Flask
from routes.products import products_bp
from routes.users import users_bp
from routes.cart import cart_bp
from routes.favorites import favorites_bp

app = Flask(__name__)


@app.route("/")
def home():
    return "API is running"


@app.route("/routes")
def routes():
    return {
        str(rule): sorted(rule.methods)
        for rule in app.url_map.iter_rules()
    }


app.register_blueprint(products_bp)
app.register_blueprint(users_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(favorites_bp)
