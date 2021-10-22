from datetime import datetime, timedelta

from flask import Blueprint, render_template, flash, request, url_for, redirect, make_response
from flask_login import current_user, login_required
from sqlalchemy.orm import aliased

from spendingtracker import db
from spendingtracker.models import Category, ProductPurchased, User
from spendingtracker.products.forms import ProductForm

productbp = Blueprint('products', __name__)


@productbp.route('/all-products', methods=['GET', "POST"])
@productbp.route('/all-products/<period>', methods=['GET', "POST"])
@login_required
def all_prod(period=None):
    all_products = ProductPurchased.all_user_products_by_period(period)

    sumprice_of_product_each_subcat = ProductPurchased.sumprice_of_product_each_subcat()

    sumprice_of_product_each_subcat_tabchart_dict = {query_res[0]: str(query_res[1]) for query_res in
                                                     sumprice_of_product_each_subcat}

    sumprice_of_product_each_maincat = ProductPurchased.sumprice_of_product_each_maincat()
    sumprice_of_product_each_maincat_piechart_dict = {query_res[0]: str(query_res[1]) for query_res in
                                                      sumprice_of_product_each_maincat}

    return render_template("all_products.html", all_products=all_products,
                           sumprice_each_maincat_piechart_dict=sumprice_of_product_each_maincat_piechart_dict,
                           sumprice_of_product_each_subcat_tabchart_dict=sumprice_of_product_each_subcat_tabchart_dict)


@productbp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    user_subcat = Category.users_all_sub_categories(curr_user=current_user)

    recent_shopping = ProductPurchased.query.filter_by(user_id=current_user.id).limit(10).all()
    form = ProductForm()
    form.cat_of_purchase.choices = [("", "---")] + [(cat.id, cat.name) for cat in user_subcat]
    if form.validate_on_submit() and request.method == 'POST':
        product = ProductPurchased(price=form.price.data, purchased_by=current_user,
                                   purchase_cat=Category.query.get(int(form.cat_of_purchase.data)),
                                   buy_date=form.purchase_date.data)
        db.session.add(product)
        db.session.commit()
        flash(f"{product.purchase_cat}, added")
        return redirect(url_for('products.add_product'))
    return render_template('add_purchase.html', form=form, recent_shopping=recent_shopping)


@productbp.route('/del-prod/<int:id>', methods=["GET", 'POST'])
@login_required
def del_prod(id):
    prod_to_del = ProductPurchased.query.get_or_404(id)
    db.session.delete(prod_to_del)
    flash(f"{prod_to_del.purchase_cat.name}, deleted")
    db.session.commit()
    return redirect(url_for('products.all_prod'))
