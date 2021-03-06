import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.client import Config as ConfigS3
from flask_wtf import CSRFProtect
from spendingtracker.config import Config, ConfigProd
from spendingtracker.error_handlers import server_error

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
csrf = CSRFProtect()
ma = Marshmallow()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
s3_client = boto3.client("s3", region_name=os.environ.get("S3_REGION_NAME"), aws_access_key_id=os.environ.get("S3_KEY"),
                         aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
                         config=ConfigS3(signature_version='s3v4'))


def create_app():
    app = Flask(__name__)
    if app.config['ENV'] == 'development':
        app.config.from_object(config.Config)
    else:
        app.config.from_object(config.ConfigProd)
    db.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    from spendingtracker import commands
    commands.init_app(app)

    from spendingtracker.models import User, Category, ProductPurchased

    from spendingtracker.main.routes import main
    from spendingtracker.users.routes import users
    from spendingtracker.category.routes import categorybp
    from spendingtracker.products.routes import productbp

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(categorybp)
    app.register_blueprint(productbp)

    # API Marshmallow
    from spendingtracker.api_rest.users_api import usersapi
    from spendingtracker.api_rest.product_api import productapi
    from spendingtracker.api_rest.category_api import categoryapi

    ma.init_app(app)

    app.register_blueprint(usersapi)
    app.register_blueprint(productapi)
    app.register_blueprint(categoryapi)
    # error handlers
    app.register_error_handler(500, server_error)

    return app
