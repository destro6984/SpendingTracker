from flask import render_template
from werkzeug.exceptions import HTTPException


def server_error(e):
  return render_template('500.html'), 500