from flask_login import UserMixin, current_user
from sqlalchemy.orm.collections import attribute_mapped_collection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from spendingtracker import db, login_manager, bcrypt
from flask import current_app
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    bought_products = db.relationship("Productpurchased", backref="purchased_by",
                                      cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}', mail '{self.email}', Image '{self.image_file}', products '{[prod.purchase_cat.name for prod in self.bought_products]}')"

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
            period='all'
        product_result = {
            "all": cls.query.filter_by(user_id=current_user.id).all(),
            "today": cls.query.filter_by(user_id=current_user.id).filter(Productpurchased.buy_date == datetime.today().date()).all(),
            "7days": cls.query.filter_by(user_id=current_user.id).filter(Productpurchased.buy_date >= (
                        datetime.now() - timedelta(days=7)).date()).all(),
            "month": cls.query.filter_by(user_id=current_user.id).filter(db.func.extract('month',Productpurchased.buy_date) == datetime.now().strftime('%m')).all(),
            "year": cls.query.filter_by(user_id=current_user.id).filter(
                db.func.extract('year', Productpurchased.buy_date) == datetime.now().strftime('%Y')).all()
        }
        return product_result[period]

    def __repr__(self):
        return f"Productpurchased(price: '{self.price}',purchase_cat: '{self.purchase_cat.name}',purchased_by: '{self.purchased_by.username}',buy_date :{self.buy_date})"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchasedproducts = db.relationship("Productpurchased", backref="purchase_cat", lazy='subquery')
    category_parent_id = db.Column(db.Integer, db.ForeignKey(id))
    name = db.Column(db.String(50), nullable=False)
    subcategories = db.relationship(
        "Category",
        cascade="all, delete-orphan",
        backref=db.backref("parent", remote_side=id, lazy='subquery'),
        collection_class=attribute_mapped_collection("name"),
    )

    def __repr__(self):
        return f'Category: id: {self.id},purchasedproducts:{[prod.purchase_cat.name for prod in self.purchasedproducts]}, parent: {self.category_parent_id},name: {self.name}, subcategories:{[subcat for subcat in self.subcategories]}#'

    def dump(self, _indent=0):
        return (
                "   " * _indent
                + repr(self)
                + "\n"
                + "".join([c.dump(_indent + 1) for c in self.subcategories.values()])
        )

    @classmethod
    def create_category(cls, name, parent):
        root_category = Category.query.first()
        if not root_category:
            root = cls(name="Root")
            db.session.add(root)
            db.session.commit()
            new_cat = cls(name=name, parent=Category.query.get(1))
        elif parent:
            new_cat = cls(name=name, parent=Category.query.get(parent.id))
        else:
            new_cat = cls(name=name, parent=Category.query.get(1))
        return new_cat
