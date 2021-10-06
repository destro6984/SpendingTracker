import random
from datetime import datetime, timedelta

import click
from flask.cli import with_appcontext

from spendingtracker import db, create_app, bcrypt, ConfigProd
from spendingtracker.models import User, Category, Productpurchased


def reset_db():
    """Creates database"""
    db.drop_all(app=create_app(config_class=ConfigProd))
    db.create_all(app=create_app(config_class=ConfigProd))
    print('db restarted')


def create_test_user():
    """Create test user"""
    with create_app().app_context():
        users = [User(username='tester1', email='tester1@wp.pl',
                      password=bcrypt.generate_password_hash('tester1').decode('utf-8')),
                 User(username='tester2', email='tester2@wp.pl',
                      password=bcrypt.generate_password_hash('tester2').decode('utf-8'))]
        db.session.add_all(users)
        db.session.commit()
        print(f"Useres: created {[user.username for user in users]}")


# @click.option('--curr_user_id')
@click.argument('curr_user_id')
def create_default_category_set(curr_user_id):
    """

    :param curr_user_id:
    :return:Create category set for user 3-subca for 1-1maincat
    """
    with create_app().app_context():
        curr_user = User.query.get(curr_user_id)
        if not curr_user or curr_user.category_set:
            print(curr_user.username)
            print('THERE ARE EXISTING CATEGORIES OR NO TEST USER')
            return None

        categories = []
        # ONLY BY THE ORDER PAY ATTENTION WHEN EDIT
        main_cats = ['Food', 'Home', 'Media', 'Clothes', 'Entertainment', 'Transport', 'Others']
        subcategories = ['Restaurants', 'Shopping-Food', 'Alcohol', 'Rent', 'Bills', 'Equipment', 'Phone', 'Internet',
                         'Netflix',
                         'Normal Staff', 'Shoes', 'Jewellery', 'Hobby', 'Cinema', 'Books', 'Fuel', 'Tickets', 'Parking',
                         'Taxes', 'Presents', 'Other Services']
        subcat_sorted = [subcategories[i * 3:(i + 1) * 3] for i in range((len(subcategories) + 3 - 1) // 3)]

        for index, cat in enumerate(main_cats):
            new_cat = Category.create_category(name=cat, parent=Category.query.get(1), curr_user_id=curr_user.id)
            categories.append(new_cat)
            for subcat in subcat_sorted[index]:
                new_subcatcat = Category.create_category(name=subcat, parent=Category.query.filter_by(name=cat).first(),
                                                         curr_user_id=curr_user_id)
                categories.append(new_subcatcat)
        db.session.add_all(categories)
        db.session.commit()
        print(f"Category set created for {curr_user.username}")


@click.option('--curr_user_id')
def create_default_shopping(curr_user_id):
    """

    :param curr_user_id:
    :return:
    """
    with create_app().app_context():
        curr_user = User.query.get(curr_user_id)
        if not curr_user:
            print('NO TEST USER')
            return None
        category_select = [cat.id for cat in Category.users_all_sub_categories(curr_user=curr_user)]

        start = datetime.now()
        end = start - timedelta(days=31)
        random_date = start + (end - start) * random.random()
        product_list = []
        for product in range(0, 11):
            purchased = Productpurchased(price=round(random.uniform(0.1, 1000), 2), purchased_by=curr_user,
                                         purchase_cat=Category.query.get(random.choice(category_select)),
                                         buy_date=random_date.strftime('%Y-%m-%d'))
            product_list.append(purchased)
        db.session.add_all(product_list)
        db.session.commit()


def init_app(app):
    # add multiple commands in a bulk
    for command in [reset_db, create_test_user, create_default_category_set, create_default_shopping]:
        app.cli.add_command(app.cli.command()(command))

# initial idea :
# https://itnext.io/use-flask-cli-to-create-commands-for-your-postgresql-on-heroku-in-6-simple-steps-e8166c024c8d
