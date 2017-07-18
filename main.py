from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "abc"

#TODO WHY DOES CSS STYLING DISSAPEAR WHEN I AM NOT LOGGED IN?

#Create class blogs, making them persistent and attaching the information to the database
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(46))
    content = db.Column(db.String(140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #Instantiate the attributes of our blog object
    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

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
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

#Requires the user to be logged in as an account user in order to make posts
@app.before_request
def require_login():
    #controls which routes a non-logged in user can view, this is based on the function name
    allowed_routes = ['login', 'register', 'blogs' , 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#ROUTE FOR HOMEPAGE, DISPLAYS ALL USERS WHO HAVE REGISTERED WITH THE APP
@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()

    return render_template('index.html',
          title="BLOG",
          users=users
          )


#THIS PAGE CONTROLS HOW THE PAGE FILTERS RESULTS BY USER OR BY ID
@app.route('/blogs', methods=['POST', 'GET'])
def blogs():


    blog_id = request.args.get('id')
    if (blog_id):
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_template.html', blogs=blogs)

    user_name = request.args.get('username')
    user_id = request.args.get('user')
    if (user_id):
        blogs = Blog.query.filter_by(owner_id=user_id)
        return render_template('single_user.html', blogs=blogs, user_name=user_name)


    blogs = Blog.query.all()
    return render_template('blogs.html',
          title="BLOG",
          blogs=blogs,
          )


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_info = User.query.filter_by(username=username).first()

        if login_info and login_info.password == password:
            session['username'] = username
            flash(username + " is logged in",'atta_boy')
            return redirect('/new_post')
        else:
            flash('User name or password incorrect, or does not exist.')

    return render_template('login.html')


#TODO when logged in, takes you to the home screen, when logged out. Takes you to the login
@app.route('/logout')
def logout():
    username = str(session['username'])
    del session['username']
    flash(username + " has been logged out", 'atta_boy')
    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #Form validation for the registration checking that the user entered something
        if username == "" or password == "" or verify == "":
            flash('Please Enter a username, password and matching verification')
            return render_template('register.html', username=username)


        # - If username exists, assign it to the variable existing_user
        existing_user = User.query.filter_by(username=username).first()


        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            #todo - Remember the user
            session['username'] = username
            flash("Registered User")
            return redirect('/new_post')
        else:
            # todo - user better response message
            flash('Duplicate User')

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
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_name, blog_content, owner)

        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()
            url = "/blogs?id=" + str(new_blog.id)
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

if __name__ == "__main__":
        app.run()
