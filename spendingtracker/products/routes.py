from flask import Blueprint, render_template, flash, request, url_for,redirect

from spendingtracker import db
from spendingtracker.category.forms import CategoryForm
from spendingtracker.models import Category, Productpurchased, User
from spendingtracker.products.forms import ProductForm

productbp=Blueprint('products', __name__)

@productbp.route('/all-products',methods=['GET',"POST"])
def all_prod():
    all_prod=Productpurchased.query.all()
    return render_template("all_products.html",all_products=all_prod)

@productbp.route('/add-product',methods=['GET','POST'])
def add_product():
    present_maincat = Category.query.filter(Category.id != 1).all()
    form=ProductForm()
    form.cat_of_purchase.choices = [("", "---")] + [(cat.id, cat.name) for cat in present_maincat]
    if form.validate_on_submit() and request.method =='POST':
        product = Productpurchased(price=form.price.data,purchased_by=User.query.get(1),purchase_cat=Category.query.get(int(form.cat_of_purchase.data)))
        db.session.add(product)
        db.session.commit()
        flash(f"{product.purchase_cat}, added")
        return redirect(url_for('products.add_product'))
    return render_template('add_purchase.html',form=form)


@productbp.route('/del-prod/<int:id>', methods=["GET",'POST'])
def del_prod(id):
    prod_to_del = Productpurchased.query.get_or_404(id)
    db.session.delete(prod_to_del)
    flash(f"{prod_to_del.purchase_cat.name}, deleted")
    db.session.commit()
    return redirect(url_for('products.all_prod'))