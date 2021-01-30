from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        'author': 'Emilio',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'August 20, 2021'
    },
    {
        'author': 'Mariela',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'August 21, 2021'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')     # form.password.data
        # is whatever user entered into the password field.
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)   # I pass the hashed
        # password.
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are able to login', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # A query parameter appears in the url equal to the route I was trying to go to
            # before being redirected. To get the url parameter, import request from flask.
            # If it exists, redirect the user to that url(parameter)
            next_page = request.args.get('next')    # next parameter in the url
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required     # Helps the app now that you need to logged in to access this route
# You also have to create login_manager.login_view = 'login' in the __init__.py ,to tell where
# login route is located. Without this, you would not be prevented from going to account
# by typing the address directly in the address bar.
def account():
    return render_template('account.html', title='Account')