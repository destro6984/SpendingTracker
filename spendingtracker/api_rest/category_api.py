from flask import Blueprint, jsonify
from flask_marshmallow.fields import fields
from flask_restful import Api

from spendingtracker import ma
from spendingtracker.models import Productpurchased, Category

categoryapi=Blueprint('category_api', __name__,url_prefix='/api')
api = Api(categoryapi)


class CategorySchema(ma.Schema):
    class Meta:
        model=Category
        fields=('id','name')


category_schema=CategorySchema()
categories_schema=CategorySchema(many=True)

@categoryapi.route('/categories',methods=['GET'])
def get_products():
    all_categories=Category.query.all()
    result=categories_schema.dump(all_categories)
    return jsonify(result)