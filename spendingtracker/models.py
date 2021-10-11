from flask_login import UserMixin, current_user
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlalchemy.orm.collections import attribute_mapped_collection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from spendingtracker import db, login_manager, bcrypt
from flask import current_app
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


user_categories = db.Table('user_cat',
                           db.Column('cat_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                           )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    bought_products = db.relationship("Productpurchased", backref="purchased_by",
                                      cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}', mail '{self.email}', Image '{self.image_file}', bought_products '{[prod.purchase_cat.name for prod in self.bought_products]}',categories_set {[cat.name for cat in self.category_set]})"

    def get_reset_token(self, expires_sce=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sce)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def generate_hash(password):
        return bcrypt.generate_password_hash(password, 10).decode("utf-8")

    @staticmethod
    def verify_hash(password, pw_hash):
        return bcrypt.check_password_hash(pw_hash, password)

    @classmethod
    def is_cat_in_category_set(cls, cat_name):
        return cls.category_set.filter(cls.category_set.any(name=cat_name))


class Productpurchased(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    buy_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.today())

    @classmethod
    def all_user_products_by_period(cls, period):
        if not period:
            period = 'all'
        product_result = {
            "all": cls.query.filter_by(user_id=current_user.id).all(),
            "today": cls.query.filter_by(user_id=current_user.id).filter(
                Productpurchased.buy_date == datetime.today().date()).all(),
            "7days": cls.query.filter_by(user_id=current_user.id).filter(Productpurchased.buy_date >= (
                    datetime.now() - timedelta(days=7)).date()).all(),
            "month": cls.query.filter_by(user_id=current_user.id).filter(
                db.func.extract('month', Productpurchased.buy_date) == datetime.now().strftime('%m')).all(),
            "year": cls.query.filter_by(user_id=current_user.id).filter(
                db.func.extract('year', Productpurchased.buy_date) == datetime.now().strftime('%Y')).all()
        }
        return product_result[period]

    @classmethod
    def sumprice_of_product_each_subcat(cls):
        sum_of_products = cls.query.with_entities(Category.name,
                                                  db.func.sum(cls.price).label(
                                                      'total')).filter(
            cls.user_id == current_user.id).outerjoin(Category, cls.product_id == Category.id).group_by(
            Category.name)
        return sum_of_products

    @classmethod
    def sumprice_of_product_each_maincat(cls):
        cat_parent = aliased(Category)
        period = {'month': db.func.extract('month', cls.buy_date) == datetime.now().strftime('%m'),
                  'year': db.func.extract('year', cls.buy_date) == datetime.now().strftime('%Y')}
        sum_of_products = cls.query.with_entities(cat_parent.name, db.func.sum(cls.price)).outerjoin(
            Category, cls.product_id == Category.id).outerjoin(cat_parent,
                                                               Category.category_parent_id == cat_parent.id).filter(
            period['month']).filter(
            cls.user_id == current_user.id).group_by(
            Category.category_parent_id, cat_parent.name).all()
        return sum_of_products

    def __repr__(self):
        return f"Productpurchased(price: '{self.price}',purchase_cat: '{self.purchase_cat.name}',purchased_by: '{self.purchased_by.username}',buy_date :{self.buy_date})"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchasedproducts = db.relationship("Productpurchased", backref="purchase_cat", lazy='subquery')
    category_parent_id = db.Column(db.Integer, db.ForeignKey(id))
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship('User', secondary=user_categories, lazy='subquery',
                            backref=db.backref('category_set', lazy=True))
    subcategories = db.relationship(
        "Category",
        cascade="all, delete-orphan",
        backref=db.backref("parent", remote_side=id, lazy='subquery'),
        collection_class=attribute_mapped_collection("name")
    )

    def __repr__(self):
        return f'Category: id: {self.id},purchasedproducts:{[prod.purchase_cat.name for prod in self.purchasedproducts]}, parent: {self.category_parent_id},name: {self.name}, current_users_subcategories:{self.users_subcategories(self.name, self)} subcategories:{[subcat for subcat in self.subcategories]} users: {[user.username for user in self.users]}#'

    def dump(self, _indent=0):
        return (
                "   " * _indent
                + repr(self)
                + "\n"
                + "".join([c.dump(_indent + 1) for c in self.subcategories.values()])
        )

    @classmethod
    def create_category(cls, name, parent, curr_user_id):
        """
            Function serves all possible cases:
                -create first-category:adding root category,parent==root
                -create sub-category: adding category with parent
                -create same-name category:append only category.users many-to-many
        :param name:
        :param parent:
        :return:
        """
        curr_user = User.query.get(curr_user_id)
        root_category = Category.query.get(1)
        already_exist_cat = Category.find_by_name(name)
        if already_exist_cat:
            curr_user.category_set.append(already_exist_cat)
            db.session.commit()
            return already_exist_cat
        if not root_category:
            root = cls(name="Root")
            db.session.add(root)
            db.session.commit()
            new_cat = cls(name=name, parent=Category.query.get(1))
        elif parent:
            new_cat = cls(name=name, parent=Category.query.get(parent.id))
        else:
            new_cat = cls(name=name, parent=Category.query.get(1))

        new_cat.users.append(curr_user)
        db.session.add(new_cat)
        db.session.commit()
        return new_cat

    @classmethod
    def is_in_user_cat_set(cls, name):
        return cls.query.filter(cls.name == name).filter(cls.users.any(id=current_user.id)).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def users_subcategories(cls, cat_name, curr_user=None):
        """

        :param cat_name:
        :param curr_user:
        :return: subcategories of particular main_category which is in current_user.category_set
        """
        cat_parent = aliased(cls)

        user_subcategories = db.session.query(cls.name).join(
            cls.parent.of_type(cat_parent)).filter(cat_parent.name == cat_name).filter(
            cls.users.any(id=curr_user.id)).filter(cat_parent.users.any(id=curr_user.id)).all()

        return [sub_cat.name for sub_cat in user_subcategories]

    @classmethod
    def users_main_categories(cls, curr_user=None):
        main_categories = cls.query.join(cls.users).filter(User.id == curr_user.id).filter(
            cls.category_parent_id == 1).all()
        return main_categories

    @classmethod
    def users_all_sub_categories(cls, curr_user=None):
        main_categories = cls.query.join(cls.users).filter(User.id == curr_user.id).filter(
            cls.category_parent_id != 1).all()
        return main_categories
