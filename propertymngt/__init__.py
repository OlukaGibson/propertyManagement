import os
from flask import Flask
from .extentions import db
from .routes import propertymngt
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(propertymngt)

    CORS(app, origins=["http://localhost:3000"])

    return app