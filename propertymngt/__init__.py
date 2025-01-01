import os
from flask import Flask
from .extentions import db,migrate
from .routes import propertymngt
from flask_cors import CORS

'''
{% .... %}
{{ .... }}
{# .... #}
'''

def create_app():
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(propertymngt)

    CORS(app, origins=["http://localhost:3000"])

    app.debug = True

    return app