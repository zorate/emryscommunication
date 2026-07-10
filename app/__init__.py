import gridfs
import pymongo
from flask import Flask
from config import Config

# Global database and GridFS references — set in create_app()
db = None
fs = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    global db, fs

    # Use a direct pymongo client for all DB access.
    # flask_pymongo 2.3.0 has a known issue where mongo.db
    # returns None both inside and outside request contexts
    # on certain Python/pymongo version combinations.
    mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/emrys_db')
    db_name   = mongo_uri.rsplit('/', 1)[-1].split('?')[0] or 'emrys_db'

    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    fs = gridfs.GridFS(db)

    # Register blueprints/routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app