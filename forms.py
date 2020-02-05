from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Email, Length


class NewUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Username", validators=[
        InputRequired(), Length(max=20)
    ])
    password = PasswordField("Password", validators=[
        InputRequired()
    ])
    email = StringField("Email", validators=[
        InputRequired(), Email(), Length(max=50)
    ])
    first_name = StringField("First Name", validators=[
        InputRequired(), Length(max=30)
    ])
    last_name = StringField("Last Name", validators=[
        InputRequired(), Length(max=30)
    ])
    is_admin = BooleanField("Admin")


class LoginForm(FlaskForm):
    """Form for logging in."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    """Form for adding feedback"""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[InputRequired()])
