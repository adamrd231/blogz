from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#TODO figure out what the heck this secret key is
app.secret_key = "abc"


#Create class blogs, making them persistent and attaching the information to the database
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(46))
    content = db.Column(db.String(140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #Instantiate the attributes of our blog object
    def __init__(self, title, content):
        self.title = title
        self.content = content

    #Keep helper functions inside of the class, this one checks that you have something in both title and content.
    def is_valid(self):
        if self.title and self.content:
            return True
        else:
            return False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(15))

    #TODO I am not super clear on this realtionship part, especially the backref portion
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


#Reroute from home index to the home page
@app.route('/', methods=['POST', 'GET'])
def re_direct():
    return redirect('/blog')


#THIS IS THE HOME PAGE
@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()

    return render_template('index.html',
          title="BLOG",
          blogs=blogs,
          )


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            redirect('/new_post')
        else:
            flash('User name or password incorrect, or does not exist.')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # - Validate the users data
        existing_user = User.query.filter_by(username=username).first()


        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            #todo - Remember the user
            session['username'] = username
            flash("logged in")
            return redirect('/new_post')
        else:
            # todo - user better response message
            return "<h1>Duplicate User</h1>"

    return render_template('register.html')


#DELETE TASKS OUT OF THE BLOG, THIS IS A BUTTON NEXT TO THE BLOG ON THE HOMEPAGE
@app.route('/delete-task', methods=['POST'])
def delete_task():

    blog_id = int(request.form['blog-id'])

    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/')


#CREATE A NEW POST, BRINGS YOU TO A NEW PAGE
@app.route('/new_post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':

        blog_name = request.form['blog']
        blog_content = request.form['content']
        new_blog = Blog(blog_name, blog_content)

        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()
            url = "/single_template?id=" + str(new_blog.id)
            return redirect(url)

        else:
            flash("Please enter both fields yo!")

            return render_template('new_post.html',
                                    category="error",
                                    blog_name=blog_name,
                                    blog_content=blog_content
                                    )
    else: # GET request
        return render_template('new_post.html')



#TEMPLATE TO CREATE BLOG PAGES, THIS IS REUSED FOR EVERY BLOG ENTRY.
@app.route('/single_template', methods=['GET'])
def single_template():

    blog_id = request.args.get('id')
    blogs = Blog.query.filter_by(id=blog_id).first()

    return render_template('single_template.html', blogs=blogs)


if __name__ == "__main__":
    app.run()
