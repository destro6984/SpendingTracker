import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from flask_restful import Api
from marshmallow import INCLUDE, ValidationError, fields, pre_load
from werkzeug.utils import secure_filename

from spendingtracker import csrf, db, ma
from spendingtracker.api_rest.product_api import ProductSchema
from spendingtracker.models import User
from spendingtracker.users.utils import allowed_file_ext, save_picture, show_image

usersapi = Blueprint("users_api", __name__, url_prefix="/api")
csrf.exempt(usersapi)
api = Api(usersapi)


# https://stackoverflow.com/questions/21509728/flask-restful-post-fails-due-csrf-protection-of-flask-wtf


class UserSchema(ma.SQLAlchemyAutoSchema):
    bought_products = fields.List(fields.Nested(ProductSchema))

    class Meta:
        model = User
        # bcrytp field acceptantce needed
        unknown = INCLUDE
        load_instance = True

    @pre_load
    def hash_password(self, in_data, **kwargs):
        in_data["password"] = User.generate_hash(in_data["password"])
        return in_data


user_schema = UserSchema(only=["id", "username", "email", "image_file"])
users_schema = UserSchema(many=True, only=["id", "username", "email", "image_file"])


@usersapi.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


@usersapi.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input Data"})
    if User.find_by_email(data.get("email")) or User.find_by_username(
        data.get("username")
    ):
        return jsonify(
            {
                "message": f"User already exists : {data.get('email'), data.get('username')}"
            }
        )
    try:
        new_user = user_schema.load(data)
    except ValidationError as exp:
        return jsonify({"message": exp.messages}), 422
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user))


@usersapi.route("/login", methods=["POST"])
def login_user():
    auth = request.authorization
    try:
        user_indb = User.find_by_username(auth.username)
        if not user_indb:
            return jsonify({"msg": "No such username"}), 401
        if User.verify_hash(password=auth.password, pw_hash=user_indb.password):
            jwt_token = create_access_token(
                identity=auth.username, expires_delta=datetime.timedelta(minutes=25)
            )
            return jsonify(token=jwt_token, logged_in_as=auth.username), 201
    except Exception as err:
        return {"message": err.args, "er": err}


@usersapi.route("/users/<int:id>", methods=["GET"])
@jwt_required()
def get_one_user(id):
    one_user = User.query.get_or_404(id)
    result = user_schema.dump(one_user)
    return jsonify(result)


@usersapi.route("/update/<int:id>", methods=["PATCH"])
@jwt_required()
def update_account(id):
    data = request.form
    user_image = request.files.get("image_file")
    sec_user_image = secure_filename(user_image.filename) if user_image else None
    user = User.query.get_or_404(id)
    changed = []
    if user_image and allowed_file_ext(sec_user_image):
        picture_file = save_picture(user_image)
        user.image_file = picture_file
        changed.append("image_file")
        # user_image.save(os.path.join(current_app.root_path, 'static/profile_pic', sec_user_image))
        # user.image_file = sec_user_image
    if data.get("email") and not User.find_by_email(data["email"]):
        user.email = data["email"]
        changed.append("email")
    db.session.commit()
    return jsonify({"message": f"Change implemented {changed}"})


@usersapi.route("/avatar/<file_name>", methods=["GET"])
@jwt_required()
def check_avat(file_name):
    return show_image(file_name)


# @usersapi.route('/avatar/<file_name>', methods=['GET'])
# @jwt_required()
# def check_avat(file_name):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename=file_name)
