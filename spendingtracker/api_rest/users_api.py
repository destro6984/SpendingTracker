from flask import Blueprint, jsonify
from flask_restful import Api

from spendingtracker import ma
from spendingtracker.models import User

usersapi=Blueprint('users_api', __name__,url_prefix='/api')
api = Api(usersapi)


class UserSchema(ma.Schema):
    class Meta:
        model=User
        fields=('id','username',"email","image_file")


user_schema=UserSchema()
users_schema=UserSchema(many=True)

@usersapi.route('/users',methods=['GET'])
def get_users():
    all_users=User.query.all()
    result=users_schema.dump(all_users)
    return jsonify(result)


