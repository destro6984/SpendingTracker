

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DecimalField, IntegerField, FloatField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    price=DecimalField("Price",validators=[DataRequired()])
    cat_of_purchase=SelectField('Choose Category')
    submit = SubmitField('Add')