from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()], widget=TextArea())