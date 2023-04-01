# config.py
import dotenv
import os

# on récupère le chemin actuel de l'application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# on charge les variables de .env
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config():
    DEBUG = os.environ.get("DEBUG")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    GARES_PER_PAGE = os.environ.get("GARES_PER_PAGE")
    SECRET_KEY = os.environ.get("SECRET_KEY")
