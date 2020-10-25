import simplejson as simplejson
from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_marshmallow.fields import fields
from flask_restful import Api

from spendingtracker import ma, db
from spendingtracker.api_rest.category_api import CategorySchema
from spendingtracker.models import Productpurchased, Category, User

productapi=Blueprint('product_api', __name__,url_prefix='/api')
api = Api(productapi)


class ProductSchema(ma.Schema):
    price= fields.Decimal()
    purchase_cat=fields.Nested(CategorySchema)
    class Meta:
        model=Productpurchased
        json_module = simplejson
        fields=('id','buy_date','price','purchase_cat')


product_schema=ProductSchema()
products_schema=ProductSchema(many=True)

@productapi.route('/products',methods=['GET'])
def get_products():
    all_products=Productpurchased.query.all()
    result=products_schema.dump(all_products)
    return jsonify(result)

@productapi.route('/add-product',methods=["POST"])
def add_product():
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # purchase_cat=Category.query.get(id)
    purchase_cat=Category.query.get(2)
    # purchased_by=current_user
    purchased_by=User.query.get(1)


    new_prod=Productpurchased(price=request.json['price'],purchased_by=purchased_by,purchase_cat=purchase_cat)
    print(new_prod)
    db.session.add(new_prod)
    # db.session.commit()
    return product_schema.jsonify(new_prod)