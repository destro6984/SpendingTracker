import os


class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/profile_pic'
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.jpeg']
    MAX_CONTENT_LENGTH = 1024 * 1024


class ConfigProd(Config):
    DEBUG = False
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_KEY = os.environ.get("S3_KEY")
    S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
