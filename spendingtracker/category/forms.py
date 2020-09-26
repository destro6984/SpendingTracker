from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    new_category= BooleanField('New Category')
    name = StringField('Name',
                        validators=[DataRequired()])
    main_category=SelectField('Choose Category',validate_choice=False)
    submit = SubmitField('Add')