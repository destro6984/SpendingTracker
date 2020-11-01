from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_marshmallow.fields import fields
from flask_restful import Api
from marshmallow import pre_dump, INCLUDE

from spendingtracker import ma, db
from spendingtracker.models import Productpurchased, Category

categoryapi = Blueprint('category_api', __name__, url_prefix='/api')
api = Api(categoryapi)





class CategorySchema(ma.Schema):
    subcategories = fields.Dict(keys=fields.Str(), values=fields.Nested(lambda: CategorySchema()))

    class Meta:
        model = Category
        fields = ('id', 'name', 'subcategories', 'parent.id')


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@categoryapi.route('/categories', methods=['GET'])
def get_categories():
    all_categories = Category.query.all()
    result = categories_schema.dump(all_categories)
    return jsonify(result)


@categoryapi.route('/add-category', methods=['GET', 'POST'])
def add_cat():
    if request.method == "POST":
        if request.json.get('new_main_cat'):
            new_category = Category(name=request.json['name'], parent=Category.query.get(1))
        else:
            new_category = Category(name=request.json['name'], parent=Category.query.get(request.json['parent_id']))
        db.session.add(new_category)
        db.session.commit()
    else:
        return "asdfasd"
    return category_schema.jsonify(new_category)

@categoryapi.route('/del-category/<int:id>', methods=['DELETE'])
def del_cat(id):
    cat_to_del = Category.query.get(id)
    db.session.delete(cat_to_del)
    db.session.commit()
    return f'Deleted {cat_to_del}'

@categoryapi.route('/update-category/<int:id>', methods=['PUT'])
def update_cat(id):
    cat_to_update= Category.query.get(id)
    cat_to_update.name=request.json['name']
    db.session.commit()
    return category_schema.jsonify(cat_to_update)

