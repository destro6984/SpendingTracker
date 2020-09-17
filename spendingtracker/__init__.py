from flask import Flask

app = Flask(__name__)

from spendingtracker.main import routes