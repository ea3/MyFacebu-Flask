from flask import Flask, render_template
import os
from dotenv import load_dotenv

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

posts = [
    {
        'author': 'Emilio',
        'title': 'Blog 1',
        'content': 'This is a post',
        'date_posted': 'January 2021'},
    {
        'author': 'Mariela',
        'title': 'Blog 2',
        'content': 'This is another post',
        'date_posted': 'February 2021'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug=True)
