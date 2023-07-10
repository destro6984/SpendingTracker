from flask import Blueprint, flash, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Api
from marshmallow import INCLUDE, ValidationError

from spendingtracker import csrf, db, jwt, ma
from spendingtracker.models import ProductPurchased, User

productapi = Blueprint("product_api", __name__, url_prefix="/api")
csrf.exempt(productapi)
api = Api(productapi)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()


class ProductSchema(ma.SQLAlchemyAutoSchema):
    # price = fields.Decimal()
    # purchase_cat = fields.Nested(CategorySchema)

    class Meta:
        model = ProductPurchased
        # fields = ('id', 'buy_date', 'price', 'purchase_cat')
        # load_instance = True
        include_fk = True
        # include_relationships=True
        unknown = INCLUDE

    # @pre_load
    # def slugify_name(self, in_data, **kwargs):
    #     # in_data["user_id"] = 1
    #     # print(User.find_by_username(current_user).one_or_none(),1)
    #     print((current_user),1)
    #     print(get_current_user(),2)
    #     return in_data


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@productapi.route("/products/all", methods=["GET"])
def get_products():
    all_products = ProductPurchased.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@productapi.route("/products", methods=["GET"])
@jwt_required()
def get_myproducts():
    result = ProductSchema(
        many=True, only=["buy_date", "id", "price", "purchase_cat.name", "user_id"]
    ).dump(current_user.bought_products)
    return jsonify(result)


@productapi.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input Data"})
    try:
        new_product = ProductSchema().load(data)
    except ValidationError as err:
        return err.messages, 422

    # purchased_by = User.query.get(1)
    # new_prod = ProductPurchased(price=request.json['price'], purchased_by=purchased_by, purchase_cat=purchase_cat)
    # db.session.add(new_prod)
    # db.session.commit()
    return product_schema.jsonify(new_product)


@productapi.route("/products/<int:id>", methods=["DELETE"])
def del_prod(id):
    prod_to_del = ProductPurchased.query.get(id)
    flash(f"Deleted {prod_to_del.purchase_cat.name}")
    db.session.delete(prod_to_del)
    db.session.commit()
    return f"Deleted Purchase: {prod_to_del.purchase_cat.name}"


@productapi.route("/products/<int:id>", methods=["PUT"])
def update_prod(id):
    prod_to_update = ProductPurchased.query.get(id)
    prod_to_update.price = request.json["price"]
    db.session.commit()
    return product_schema.jsonify(prod_to_update)
