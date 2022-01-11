from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import (
    StringField, 
    IntegerField
)
from wtforms.validators import DataRequired


class AddForm(Form):
    question = StringField('question', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])
    difficulty = IntegerField('difficulty', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    

class SearchForm(Form):
    searchTerm = StringField('searchTerm', validators=[DataRequired()])
