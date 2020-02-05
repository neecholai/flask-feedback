"""Models for Feedback app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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

    feedbacks = db.relationship('Feedback', backref='user',
                                cascade='all, delete-orphan')

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register User with hash password and return new User instance"""

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf8")
        
        new_user = cls(username=username, password=hashed_pw, email=email,
                       first_name=first_name, last_name=last_name)

        return new_user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate User"""

        user = User.query.filter(User.username == username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        
        return False


class Feedback(db.Model):
    """ Create feedback class """

    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'))

        
