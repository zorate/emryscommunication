import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-fallback-key')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/emrys_db')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')