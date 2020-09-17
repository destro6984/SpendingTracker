import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////site.db'
db = SQLAlchemy(app)

from spendingtracker.main.routes import main
from spendingtracker.products import routes
from spendingtracker.users import routes

app.register_blueprint(main)
