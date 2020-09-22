from flask_login import UserMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from spendingtracker import db, app, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    bought_products=db.relationship("Productpurchased",backref="purchased_by",lazy=True,cascade = "all, delete-orphan" )

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}','{self.bought_products}')"

    def get_reset_token(self, expires_sce=1800):
        s= Serializer(app.config['SECRET_KEY'],expires_sce)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s= Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Productpurchased(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10,2),nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("category.id"),nullable=False)
    buy_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.utcnow)

    def __repr__(self):
        return f"User(price: '{self.price}',purchase_cat: '{self.purchase_cat}',purchased_by: '{self.purchased_by}',buy_date :{self.buy_date})"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.relationship("Productpurchased", uselist=False, backref="purchase_cat")
    category_parent_id = db.Column(db.Integer, db.ForeignKey(id))
    name = db.Column(db.String(50), nullable=False)
    subcategories = db.relationship(
        "Category",
        cascade="all, delete-orphan",
        backref=db.backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )

    def __repr__(self):
        return "Category(name=%r, id=%r, parent_id=%r)" % (
            self.name,
            self.id,
            self.category_parent_id,
        )

    def dump(self, _indent=0):
        return (
                "   " * _indent
                + repr(self)
                + "\n"
                + "".join([c.dump(_indent + 1) for c in self.subcategories.values()])
        )