import os

from dotenv import find_dotenv, load_dotenv


class Config:
    load_dotenv(find_dotenv("./spendingtracker/.env"), verbose=True)
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@localhost/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "static/profile_pic"
    UPLOAD_EXTENSIONS = [".jpg", ".png", ".jpeg"]
    MAX_CONTENT_LENGTH = 1024 * 1024
    SESSION_COOKIE_SECURE = False


class ConfigProd(Config):
    DEBUG = False
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_KEY = os.environ.get("S3_KEY")
    S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")
    uri = os.environ.get("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
