from flask import Blueprint, render_template, flash, request

from spendingtracker import db
from spendingtracker.category.forms import CategoryForm
from spendingtracker.models import Category, Productpurchased

productbp=Blueprint('products', __name__)

@productbp.route('/add-product',methods=['GET','POST'])
def add_cat():
    return render_template('add_product.html')


@productbp.route('/all-products',methods=['GET',"POST"])
def all_prod():
    all_prod=Productpurchased.query.all()
    return render_template("all_products.html",all_products=all_prod)

@productbp.route('/del-prod/<int:id>', methods=["GET",'POST'])
def del_prod(id):
    prod_to_del = Productpurchased.query.get(id)
    db.session.delete(prod_to_del)
    db.session.commit()
    flash(f"{prod_to_del.id}, deleted")
    return render_template('all_products.html')