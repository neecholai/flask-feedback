"""Models for Feedback app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from random import choice
from string import ascii_letters

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    pw_reset_token = db.Column(db.Text)

    feedbacks = db.relationship('Feedback', backref='user',
                                cascade='all, delete-orphan')

    @classmethod
    def register(cls, username, password, email, first_name, last_name, is_admin):
        """Register User with hash password and return new User instance"""

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf8")

        new_user = cls(username=username, password=hashed_pw, email=email,
                       first_name=first_name, last_name=last_name, is_admin=is_admin)

        return new_user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate User"""

        user = User.query.filter(User.username == username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user

        return False

    @classmethod
    def generate_reset_token(cls, email):
        """Generate token for password reset"""

        user = User.query.filter(User.email == email).first()

        random_token = randomString(8)
        hashed_token = bcrypt.generate_password_hash(random_token).decode("utf8")

        user.pw_reset_token = hashed_token
        db.session.commit()

        return [user.username, random_token]

    @classmethod
    def validate_reset_token(cls, username, token):

        user = User.query.filter(User.username == username).first()
        if user and bcrypt.check_password_hash(user.token, token):
            return user

        return False
    
    @classmethod
    def update_password(cls, username, password):

        user = User.query.filter(User.username == username).first()

        if bcrypt.check_password_hash(user.password, password):
            return False

        new_hashed_pw = bcrypt.generate_password_hash(password).decode("utf8")
        user = User.query.filter(User.username == username).first()

        user.password = new_hashed_pw
        user.pw_reset_token
        db.session.commit()

        return user


class Feedback(db.Model):
    """ Create feedback class """

    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'))


def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """

    letters = ascii_letters
    return ''.join(choice(letters) for i in range(stringLength))
