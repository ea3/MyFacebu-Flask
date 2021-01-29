from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # assigned automatically.
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # Provided by default if not given.
    password = db.Column(db.String(60), nullable=False)
    # One to many relationship. One user can have multiple posts but a post
    # can only have one author .
    posts = db.relationship('Post', backref='author', lazy=True)
    # the posts relationship allows us to get all the posts for an user.
    # Backref uses this author attribute to get the user who created the post.
    # Lazy parameter loads the data from the db in one go as necessary.

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)       # remember to NOT use parenthesis in utcnow.
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user_if is the foreign key. Uses the id of the user.
    # After creating the models, create the db in the terminal from app import db. db.create_all() creates
    # the db file in the project structure .

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
