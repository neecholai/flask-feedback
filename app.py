"""Flask app for Feedback"""

from flask import Flask, render_template, redirect 
from models import db, connect_db, User
from forms import UserForm


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

    form = UserForm()

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
        except Exception as e:
            return f"Error: {e}"

        return redirect('/secret')

    return render_template('register.html', form=form)


@app.route('/secret')
def secret():

    return "YOU MADE IT"
