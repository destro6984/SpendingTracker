import datetime
import os

from flask import Blueprint, jsonify, request, url_for, send_from_directory, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_current_user
from flask_restful import Api
from marshmallow import fields, INCLUDE
from flask_login import current_user
from werkzeug.utils import secure_filename

from spendingtracker import ma, db, app
from spendingtracker.api_rest.product_api import ProductSchema
from spendingtracker.models import User
from spendingtracker.users.utils import allowed_file_ext

usersapi = Blueprint('users_api', __name__, url_prefix='/api')
api = Api(usersapi)


class UserSchema(ma.Schema):
    bought_products = fields.List(fields.Nested(ProductSchema))

    class Meta:
        model = User
        fields = ('id', 'username', "email", "image_file", "bought_products")
        # bcrytp field acceptantce needed
        unknown = INCLUDE


user_schema = UserSchema(only=['id', 'username', 'email', 'image_file'])
users_schema = UserSchema(many=True, only=['id', 'username', 'email', 'image_file'])


@usersapi.route('/users', methods=['GET'])
@jwt_required
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    current_user = get_jwt_identity()
    return jsonify(result)


@usersapi.route('/register', methods=['POST'])
def register():
    data = request.json
    data['password'] = User.generate_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user))


@usersapi.route('/login', methods=['POST'])
def login_user():
    auth = request.authorization
    try:
        curr_user = User.find_by_username(auth.username)
        if not curr_user:
            return jsonify({"msg": "No such username"}), 401
        if User.verify_hash(password=auth.password, pw_hash=curr_user.password):
            jwt_token = create_access_token(identity=auth.username, expires_delta=datetime.timedelta(minutes=25))
            return jsonify(token=jwt_token, logged_in_as=auth.username), 201
    except Exception as err:
        return {"message": err.args,
                'er': err}


@usersapi.route('/user/<int:id>', methods=['GET'])
@jwt_required
def get_one_user(id):
    one_user = User.query.filter_by(id=id).first()
    result = user_schema.dump(one_user)
    return jsonify(result)


@usersapi.route('/update/<int:id>', methods=['PATCH'])
@jwt_required
def update_account(id):
    data = request.form
    user_image = request.files['image_file']
    sec_user_image = secure_filename(user_image.filename)
    user = User.query.get_or_404(id)
    if user_image and allowed_file_ext(sec_user_image):
        user_image.save(os.path.join(current_app.root_path, 'static/profile_pic', sec_user_image))
        user.image_file = sec_user_image
    if data['email'] and not User.find_by_email(data['email']):
        user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'Change implemented email'})


@usersapi.route('/avatar/<file_name>', methods=['GET'])
@jwt_required
def check_avat(file_name):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename=file_name)
