import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, mail
from app.forms import (RegistrationForm, LoginForm, UpdateAccountForm, \
                       PostForm, RequestResetForm, ResetPasswordForm)
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    # Grab the page that I want get it from a query parameter in the url.
    # Page is an optional parameter in the url. type int to prevent user from passing non ints.
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # form.password.data
        # is whatever user entered into the password field.
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)  # I pass the hashed
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
            next_page = request.args.get('next')  # next parameter in the url
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    # Dont save the name of the file being upload, might collide with other files in the db with the same name.
    # Import secrets, 8  are the bytes. Grab file extension. Import os
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # Using pillow package to resize image.
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required  # Helps the app now that you need to logged in to access this route
# You also have to create login_manager.login_view = 'login' in the __init__.py ,to tell where
# login route is located. Without this, you would not be prevented from going to account
# by typing the address directly in the address bar.
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        # POST-GET redirect pattern. Reloading browser after submitting your form. Redirecting sends a GET request.
        return redirect(url_for('account'))
    elif request.method == 'GET':
        # populates the date in the form.
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Create Post')


@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post_ = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post_.title, post=post_)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post_ = Post.query.get_or_404(post_id)
    if post_.author != current_user:
        # 403 is the Forbidden route response
        abort(403)
    form = PostForm()
    # Populate form with the current post title and content. Same as in the account page with the account info.
    if form.validate_on_submit():
        post_.title = form.title.data
        post_.content = form.content.data
        # When the information is already in the db, there is no need to db.session.add().
        # We are only updating the information already in the db.
        db.session.commit()
        flash('Your has been updated!', 'success')
        return redirect(url_for('post', post_id=post_.id))
    elif request.method == 'GET':
        form.title.data = post_.title
        form.content.data = post_.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post_ = Post.query.get_or_404(post_id)
    if post_.author != current_user:
        # 403 is the Forbidden route response
        abort(403)
    db.session.delete(post_)
    db.session.commit()
    flash('Your has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_post(username):
    page = request.args.get('page', 1, type=int)
    # Get the user.
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=3)
    return render_template('user_post.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='devea3test@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request please ignore this email. 
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    # User must be logged out before resetting their passwords.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('AN email has been sent instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    # User must be logged out before resetting their passwords.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # form.password.data
        # is whatever user entered into the password field.
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated. You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
