"""Flask app for Feedback"""

from flask import Flask, render_template, redirect, flash, session
from models import db, connect_db, User
from forms import NewUserForm, LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = "DHFGUSRGHUISHGUISHG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
db.create_all()

@app.route('/')
def root():

    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def add_user():

    form = NewUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        

        # Email isssue validation here 
        try: 
            db.session.commit()
        except Exception:
            flash("username or email already exists")
            return render_template('register.html', form=form)

        return redirect('/secret')

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['user_id'] = user.id
            return redirect('/secret')
        else:
            flash("Invalid username or password!")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/secret')
def secret():

    return "YOU MADE IT"
