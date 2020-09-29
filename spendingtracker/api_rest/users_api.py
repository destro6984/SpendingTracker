from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import fields

from spendingtracker import ma
from spendingtracker.api_rest.product_api import ProductSchema
from spendingtracker.models import User

usersapi=Blueprint('users_api', __name__,url_prefix='/api')
api = Api(usersapi)


class UserSchema(ma.Schema):
    bought_products=fields.List(fields.Nested(ProductSchema))
    class Meta:
        model=User
        fields=('id','username',"email","image_file","bought_products")


user_schema=UserSchema()
users_schema=UserSchema(many=True)

@usersapi.route('/users',methods=['GET'])
def get_users():
    all_users=User.query.all()
    result=users_schema.dump(all_users)
    return jsonify(result)


