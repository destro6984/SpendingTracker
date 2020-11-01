from flask import Blueprint, render_template, flash, request, url_for,redirect

from spendingtracker import db
from spendingtracker.category.forms import CategoryForm
from spendingtracker.models import Category

categorybp=Blueprint('category', __name__)

@categorybp.route('/add-category',methods=['GET','POST'])
def add_cat():
    present_maincat=Category.query.filter_by(category_parent_id=1).all()
    form=CategoryForm()
    form.main_category.choices=[("", "---")]+[(cat.id,cat.name) for cat in present_maincat]
    if form.validate_on_submit() and request.method =='POST':
        if form.new_category.data:
            category=Category(name=form.name.data,parent=Category.query.get(1))
        else:
            category = Category(name=form.name.data, parent=Category.query.get(int(form.main_category.data)))
        db.session.add(category)
        db.session.commit()
        flash(f"{category.name}, added")
        return redirect(url_for('category.add_cat'))
    return render_template('add_category.html',form=form,present_cat=present_maincat)


@categorybp.route('/all-category',methods=['GET',"POST"])
def all_cat():
    all_cat=Category.query.all()
    return render_template("all_category.html",all_cat=all_cat)

@categorybp.route('/del-cat/<int:id>', methods=["GET",'POST'])
def del_cat(id):
    cat_to_del = Category.query.get_or_404(id)
    flash(f"{cat_to_del.name}, deleted")
    return redirect(url_for('category.all_cat'))