from flask import Blueprint, render_template

from spendingtracker import db
from spendingtracker.category.forms import CategoryForm
from spendingtracker.models import Category

categorybp=Blueprint('category', __name__)

@categorybp.route('/add-category',methods=['GET','POST'])
def add_cat():
    present_maincat=Category.query.filter_by(category_parent_id=1).all()
    form=CategoryForm()
    form.main_category.choices=[("", "---")]+[(cat.id,cat.name) for cat in present_maincat]
    if form.validate_on_submit():
        if form.new_category.data:
            category=Category(name=form.name.data,parent=Category.query.get(1))
        else:
            category = Category(name=form.name.data, parent=Category.query.get(int(form.main_category.data)))
        db.session.add(category)
        db.session.commit()
    return render_template('add_category.html',form=form,present_cat=present_maincat)
