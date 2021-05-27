import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    UPLOAD_FOLDER='static/profile_pic'
    UPLOAD_EXTENSIONS= ['.jpg','.png','.jpeg']
    MAX_CONTENT_LENGTH= 1024 * 1024