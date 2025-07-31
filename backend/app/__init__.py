from flask import Flask
from flask_cors import CORS
from .db import mysql
from .routes.portfolio import portfolio_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')
    mysql.init_app(app)
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    return app
