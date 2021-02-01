from flask import render_template, request, Blueprint
from app.models import Post


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    # Grab the page that I want get it from a query parameter in the url.
    # Page is an optional parameter in the url. type int to prevent user from passing non ints.
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title='About')


