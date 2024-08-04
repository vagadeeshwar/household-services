import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "a-secret-key"
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUDIO_FOLDER = "/Users/vagadeeshwar/Desktop/MAD_Files/Audio_Files"
    IMAGE_FOLDER = "/Users/vagadeeshwar/Desktop/MAD_Files/Image_Files"


class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "../database.sqlite3")
    DEBUG = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "../database.sqlite3")
    DEBUG = False
