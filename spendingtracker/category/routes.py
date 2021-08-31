from flask import Blueprint, render_template, flash, request, url_for, redirect
from flask_login import login_required

from spendingtracker import db
from spendingtracker.category.forms import CategoryForm
from spendingtracker.models import Category

categorybp = Blueprint('category', __name__)


@categorybp.route('/add-category', methods=['GET', 'POST'])
@login_required
def add_cat():
    main_categories = Category.query.filter_by(category_parent_id=1).all()
    form = CategoryForm()
    form.main_category.choices = [("", "---")] + [(cat.id, cat.name) for cat in main_categories]
    if form.validate_on_submit() and request.method == 'POST':
        main_category_id = int(form.main_category.data) if form.main_category.data else None
        category = Category.create_category(name=form.name.data.capitalize(),
                                            parent=Category.query.get(main_category_id))
        db.session.add(category)
        db.session.commit()
        flash(f"Added new Category : {category.name}", "info")
        return redirect(url_for('category.add_cat'))
    return render_template('add_category.html', form=form, main_categories=main_categories)


@categorybp.route('/all-category', methods=['GET', "POST"])
@login_required
def all_cat():
    all_cat = Category.query.all()
    return render_template("all_category.html", all_cat=all_cat)


@categorybp.route('/del-cat/<name>', methods=["GET", 'POST'])
@login_required
def del_cat(name):
    if name == 'Root':
        flash(f"Cannot Delete this category: {name}", 'danger')
        return redirect(url_for('category.add_cat'))
    cat_to_del = Category.query.filter_by(name=name).first_or_404()
    db.session.delete(cat_to_del)
    db.session.commit()
    flash(f"Category Deleted : {cat_to_del.name}", 'danger')
    return redirect(url_for('category.add_cat'))
