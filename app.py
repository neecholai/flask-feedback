"""Flask app for Feedback"""

from flask import Flask, render_template, redirect, flash, session, abort
from models import db, connect_db, User, Feedback
from forms import NewUserForm, LoginForm, FeedbackForm, ForgetPasswordForm, ResetPasswordForm
from flask_mail import Message, Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = "DHFGUSRGHUISHGUISHG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

mail_settings = {
    "MAIL_SERVER": 'smtp@gmail.com',
    "MAIL_PORT": 465,  # perhaps port 587 if this doesn't work
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'nicholaihansen22@gmail.com',
    "MAIL_PASSWORD": '?LghtnP3532?'
}

app.config.update(mail_settings)
mail = Mail(app)
mail.init_app(app)

connect_db(app)
db.create_all()


@app.route('/')
def root():
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def add_user():

    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
        return redirect(f"/users/{user.username}")

    form = NewUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        is_admin = form.is_admin.data

        new_user = User.register(
            username, password, email, first_name, last_name, is_admin)
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
    """Login an existing user."""

    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        return redirect(f"/users/{user.username}")

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
    logged_in_user = User.query.get(user_id)

    try:
        user = User.query.filter(User.username == username).one()
    except Exception:
        abort(404)

    if user_id == user.id or logged_in_user.is_admin:
        user = User.query.get(user.id)
        return render_template('user.html', user=user, feedbacks=user.feedbacks)

    else:
        abort(401)


@app.route('/logout')
def logout():
    """ Logs out user and redirects to home page """

    session.pop('user_id')
    return redirect('/')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """ Delete User """

    user_id = session.get('user_id')
    logged_in_user = User.query.get(user_id)

    try:
        user = User.query.filter(User.username == username).one()
    except Exception:
        abort(404)

    if user_id != user.id and not logged_in_user.is_admin:
        abort(401)

    db.session.delete(user)
    db.session.commit()
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """ Add feedback """

    form = FeedbackForm()

    user_id = session.get('user_id')
    logged_in_user = User.query.get(user_id)

    try:
        user = User.query.filter(User.username == username).one()
    except Exception:
        abort(404)

    if user_id != user.id and not logged_in_user.is_admin:
        abort(401)

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
    logged_in_user = User.query.get(user_id)

    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.user

    if user_id != user.id and not logged_in_user.is_admin:
        abort(401)

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
    logged_in_user = User.query.get(user_id)

    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.user

    if user_id != user.id and not logged_in_user.is_admin:
        abort(401)

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{user.username}')


@app.route('/password/forget', methods=["GET", "POST"])
def forget_password():

    form = ForgetPasswordForm()

    if form.validate_on_submit():

        user = User.query.filter(User.email == form.email.data).first()

        if user:

            [username, token] = User.generate_reset_token(user.email)

            msg = Message(
                        subject="Hello",
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=[user.email],
                        body=f""" Reset password with this link ->
                        http://localhost:5000/password/reset/{username}/{token}""",
                        html='<b>HTML</b>')

            with app.app_context():
                mail.send(msg)

            flash("Please check email for link to reset your password.")
            return redirect('/password/forget', form=form)

        else:
            flash('not a valid email')
            return redirect('/password/forget')

    return render_template('forget-password.html', form=form)


@app.route('/password/reset/<username>/<token>')
def update_password_form(username, token):

    user = User.validate_reset_token(username, token)
    form = ResetPasswordForm()

    if user:
        render_template('reset-password.html', form=form, user=user)
    else:
        abort(401)


@app.route('/password/reset/<username>', methods=["POST"])
def reset_password(username):

    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        user = User.update_password(username, password)

        return redirect('/login')
        