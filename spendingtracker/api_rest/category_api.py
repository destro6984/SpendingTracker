from flask import Blueprint, jsonify
from flask_marshmallow.fields import fields
from flask_restful import Api
from marshmallow import pre_dump

from spendingtracker import ma
from spendingtracker.models import Productpurchased, Category

categoryapi=Blueprint('category_api', __name__,url_prefix='/api')
api = Api(categoryapi)

#
# class IngredientSchema(ma.Schema):
#     class Meta:
#         model = Category


class CategorySchema(ma.Schema):
    subcategories = fields.Dict(keys=fields.Str(),values=fields.Nested(lambda:CategorySchema()))
    class Meta:
        model=Category
        fields=('id','name','subcategories',"parent.id")


category_schema=CategorySchema()
categories_schema=CategorySchema(many=True)

@categoryapi.route('/categories',methods=['GET'])
def get_products():
    all_categories=Category.query.all()
    result=categories_schema.dump(all_categories)
    return    jsonify(result)

