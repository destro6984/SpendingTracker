import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DecimalField, IntegerField, FloatField, \
    DateField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    price = DecimalField("Price", validators=[DataRequired(message="Remember about correct format")],
                         render_kw={"placeholder": "100.0"})
    cat_of_purchase = SelectField('Choose Category')
    purchase_date = DateField('When bought', format='%d/%m/%Y', description='Time that the event will occur',
                              default=datetime.datetime.today())
    submit = SubmitField('Add')
