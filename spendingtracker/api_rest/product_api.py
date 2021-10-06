import simplejson as simplejson
from flask import Blueprint, jsonify, request, flash
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_marshmallow.fields import fields
from flask_restful import Api

from spendingtracker import ma, db
from spendingtracker.api_rest.category_api import CategorySchema
from spendingtracker.models import Productpurchased, Category, User

productapi = Blueprint('product_api', __name__, url_prefix='/api')
api = Api(productapi)


class ProductSchema(ma.Schema):
    price = fields.Decimal()
    purchase_cat = fields.Nested(CategorySchema)

    class Meta:
        model = Productpurchased
        json_module = simplejson
        fields = ('id', 'buy_date', 'price', 'purchase_cat')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@productapi.route('/products', methods=['GET'])
def get_products():
    all_products = Productpurchased.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@productapi.route('/my-products', methods=['GET'])
@jwt_required()
def get_myproducts():
    current_user = User.find_by_username(get_jwt_identity())
    result = products_schema.dump(current_user.bought_products)
    return jsonify(result)


@productapi.route('/add-product', methods=["POST"])
def add_product():
    # purchase_cat=Category.query.get(id)
    purchase_cat = Category.query.get(2)
    # purchased_by=current_user
    purchased_by = User.query.get(1)
    new_prod = Productpurchased(price=request.json['price'], purchased_by=purchased_by, purchase_cat=purchase_cat)
    db.session.add(new_prod)
    db.session.commit()
    return product_schema.jsonify(new_prod)

@productapi.route('/del-product/<int:id>', methods=['DELETE'])
def del_prod(id):
    prod_to_del = Productpurchased.query.get(id)
    flash(f'Deleted {prod_to_del.purchase_cat.name}')
    db.session.delete(prod_to_del)
    db.session.commit()
    return f'Deleted Purchase: {prod_to_del.purchase_cat.name}'

@productapi.route('/update-product/<int:id>', methods=['PUT'])
def update_prod(id):
    prod_to_update= Productpurchased.query.get(id)
    prod_to_update.price=request.json['price']
    db.session.commit()
    return product_schema.jsonify(prod_to_update)
