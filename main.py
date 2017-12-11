from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:P@ssword1@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'open_sesame'


class Blog(db.Model):
    '''
    Store blog posts
    '''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.String(2000))
    created = db.Column(db.DateTime)

    def __init__(self, title, body ):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()

    def is_valid(self):
        if self.title and self.body and self.created:
            return True
        else:
            return False


@app.route("/blog")
def display_blog_posts():
    '''
    Either list one entry with the given ID
    Or list all blog entries (in default or newest order)
    '''
    # TODO refactor to use routes with variables instead of GET parameters
    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('blog.html', title="Blog Entry", blog=blog)

    # if we're here, we need to display all the entries
    # TODO store sort direction in session[] so we remember user's preference
    sort = request.args.get('sort')
    if (sort=="newest"):
        all_posts = Blog.query.order_by(Blog.created.desc()).all()
    else:
        all_posts = Blog.query.all()   
    return render_template('all_posts.html', title="All Posts", all_posts=all_posts)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    '''
    GET: Display form for new blog entry
    POST: create new entry or redisplay form if values are invalid
    '''
    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        new_post = Blog(new_post_title, new_post_body)

        if new_post.is_valid():
            db.session.add(new_post)
            db.session.commit()

            # display just this most recent blog entry
            url = "/blog?id=" + str(new_post.id)
            return redirect(url)
        else:
            flash("Please check your entry for errors. Both a title and a body are required.")
            return render_template('new_post_form.html',
                title="Create new blog post",
                new_post_title=new_post_title,
                new_post_body=new_post_body)

    else: # GET request
        return render_template('new_post_form.html', title="Create new blog post")


@app.route("/")
def index():
    '''
    Displays all posts
    '''
    return redirect("/blog")


if __name__ == '__main__':
    app.run()