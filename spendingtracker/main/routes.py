from flask import Blueprint

from spendingtracker import app


main=Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def hello_world():
    return 'Hello, World!'