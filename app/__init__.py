import gridfs
from flask import Flask
from flask_pymongo import PyMongo
from config import Config

# Global extensions
mongo = PyMongo()
fs = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize PyMongo
    mongo.init_app(app)

    # Initialize GridFS using the underlying pymongo database instance object
    global fs
    with app.app_context():
        fs = gridfs.GridFS(mongo.db)

    # Register blueprints/routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app