import os

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.client import Config

from spendingtracker.config import Config as cfg, ConfigProd

app = Flask(__name__)
app.config.from_object(cfg)

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

ma = Marshmallow()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
admin = Admin(name='spentrc', template_mode='bootstrap3')
s3_client = boto3.client("s3",region_name=os.environ.get("S3_REGION_NAME"), aws_access_key_id=os.environ.get("S3_KEY"),
                         aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
                         config=Config(signature_version='s3v4'))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    admin.init_app(app)

    from spendingtracker.models import User, Category, Productpurchased

    admin.add_view(ModelView(User, db.session))
    # admin.add_view(ModelView(Category, db.session))
    admin.add_view(ModelView(Productpurchased, db.session))

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

    return app
