"""Flask app for Feedback"""

from flask import Flask, render_template, redirect, flash, session, abort
from models import db, connect_db, User, Feedback
from forms import NewUserForm, LoginForm, FeedbackForm


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

        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)

        try:
            db.session.commit()
        except Exception:
            flash("username or email already exists")
            return render_template('register.html', form=form)

        session['user_id'] = new_user.id
        return redirect(f'/users/{new_user.username}')

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
            return redirect(f'/users/{user.username}')
        else:
            flash("Invalid username or password!")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/users/<username>')
def display_user(username):
    """
    Display user if login or user creation is valid.
    Return 404 error if user is not logged in.
    """

    user_id = session.get('user_id')
    user = User.query.filter(User.username == username).one()

    if user_id == user.id:
        user = User.query.get(user_id)
        return render_template('user.html', user=user, feedbacks=user.feedbacks)

    else:
        abort(404)


@app.route('/logout')
def logout():
    """ Logs out user and redirects to home page """

    session.pop('user_id')
    return redirect('/')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """ Delete User """

    user_id = session.get('user_id')
    user = User.query.filter(User.username == username).one()

    if user_id != user.id:
        abort(404)

    db.session.delete(user)
    db.session.commit()
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """ Add feedback """

    form = FeedbackForm()

    user_id = session.get('user_id')
    user = User.query.filter(User.username == username).one()

    if user_id != user.id:
        abort(404)

    if form.validate_on_submit():

        feedback = {
            "title": form.title.data,
            "content": form.content.data,
            "username": username
        }

        new_feedback = Feedback(**feedback)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f"/users/{username}")

    return render_template('feedback-form.html', user=user, form=form,
                           action=f'/users/{username}/feedback/add')


@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """ Update Feedback """

    form = FeedbackForm()

    user_id = session.get('user_id')
    feedback = Feedback.query.get(feedback_id)
    user = feedback.user

    if user_id != user.id:
        abort(404)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{user.username}')

    form.title.data = feedback.title
    form.content.data = feedback.content

    return render_template('feedback-form.html', user=user, form=form,
                           action=f'/feedback/{feedback_id}/update')


@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """ Delete Feedback """

    user_id = session.get('user_id')
    feedback = Feedback.query.get(feedback_id)
    user = feedback.user

    if user_id != user.id:
        abort(404)

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{user.username}')

