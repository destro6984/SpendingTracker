from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired()])
    main_category = SelectField('Choose for subcategory', validate_choice=False)
    submit = SubmitField('Add')
