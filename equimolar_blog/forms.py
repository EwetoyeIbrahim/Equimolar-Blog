from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,\
    SubmitField, TextAreaField, DateField
from wtforms.validators import ValidationError, DataRequired, \
    Email, Length, EqualTo
from .models import User
from datetime import datetime

class ArticleForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(),Length(max=100),],)
    slug = StringField('slug', validators=[Length(max=100),],)
    summary = StringField('summary', validators=[Length(max=100),],)
    content = TextAreaField('content', validators=[DataRequired(),],)
    last_mod_date = DateField('PublishDate', validators=[DataRequired(),],
        default=datetime.date(datetime.utcnow()))
    tags = StringField('tags', validators=[DataRequired()])
    draft = BooleanField('draft', default=False)
    submit = SubmitField('submit')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
