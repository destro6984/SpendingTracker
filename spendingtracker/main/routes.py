from flask import Blueprint, render_template, current_app

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    map_site = ['%s' % rule for rule in current_app.url_map.iter_rules()]
    return render_template("layout.html", mapsite=[])
