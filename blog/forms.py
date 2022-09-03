from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea

class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])

class UserRegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    repeat_password = StringField('repeat_password', validators=[DataRequired(), EqualTo('password')])

class UserLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])

class CommentForm(FlaskForm):
    body = TextAreaField('body', validators=[DataRequired()])