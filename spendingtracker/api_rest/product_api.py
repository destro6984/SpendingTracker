import simplejson as simplejson
from flask import Blueprint, jsonify
from flask_marshmallow.fields import fields
from flask_restful import Api

from spendingtracker import ma
from spendingtracker.models import  Productpurchased

productapi=Blueprint('product_api', __name__,url_prefix='/api')
api = Api(productapi)


class Product(ma.Schema):
    price= fields.Decimal()
    class Meta:
        model=Productpurchased
        json_module = simplejson
        fields=('id','buy_date','price')


product_schema=Product()
products_schema=Product(many=True)

@productapi.route('/products',methods=['GET'])
def get_products():
    all_products=Productpurchased.query.all()
    result=products_schema.dump(all_products)
    return jsonify(result)