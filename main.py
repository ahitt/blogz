from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = '12345'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key= True) 
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()
        self.owner = owner

#create user class with id, username, and password
class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(120), unique= True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#user must login before making new post
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'display_posts', 'index'] #if user isn't looged in can still view these pages
    print(session)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

#allows user to login, if data validates
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST': #someone is trying to login
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        users = User.query.all()

        #if user tries to login with a username not stored in the database
        #redirected to /login page
        if user not in users:
            error = 'User does not exist'
            return render_template('login.html', error=error)
        
        #if user enters a username stored in database with the correct password
        #redirected to the /newpost page with their username being stored in a session
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        #if user enters a username stored in database with an incorrect password 
        #redirected to the /login page 
        else:
            error = "Username or password is incorrect"
            return render_template('login.html', error=error)
    
    return render_template('login.html')


#user may signup for an account, if data validates 
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username_error = ""
        existing_error= ""
        password_error = ""
        match_error = ""

        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        #username character check 
        if len(username) < 3:
            username = ''
            username_error = 'Username must be more than three characters'
        elif len(username) > 20: 
            username = ''
            username_error = 'Username must be less than twenty characters'
        else:
            username=username
        
        #password character check 
        if 20 < len(password) < 3:
            password=''
            password_error= 'Password must be between three and twenty characters'
        
        #verify_password match check 
        if password != verify_password:
            password = ''
            verify_password = ''
            match_error = 'Passwords do not match'
        
        #empty fields 
        if username == '':
            username_error = 'Username must be between three and twenty characters'
        if password == '':
            password_error = 'Password must be between three and twenty characters'
        if verify_password == '':
            match_error = 'Passwords do not match'

        #if username is taken check 
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            existing_error = "Username is taken"

        if not existing_user and not username_error and not password_error and not match_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session ['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', 
                                    existing_error=existing_error,
                                    username_error=username_error,
                                    password_error=password_error,
                                    match_error=match_error)
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

#displays all the blog posts with user's name and link to their individual page
@app.route('/blog', methods = ['GET'])
def display_posts():
    entry_id = request.args.get('id')
    userid= request.args.get('userid')

    if entry_id:
        entry = Blog.query.get(entry_id)

        return render_template('entry.html', entry=entry)
    
    if userid:
        user_posts = Blog.query.filter_by(owner_id=userid).all()
        return render_template('singleUser.html', user_posts=user_posts)
    
    posts = Blog.query.order_by(desc(Blog.pub_date))
    return render_template('blog.html', posts=posts)

#creates new blog posts, if data validates
@app.route('/newpost', methods =['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['entry']

        title_error=''
        entry_error = ''

        if title == "" or entry == "":
            if title == "":
                title_error = "Enter a title"
            if entry == "":
                entry_error = "Enter a body for the post"
            return render_template('newpost.html', title=title, entry=entry, entry_error=entry_error, title_error=title_error)
        else:
            owner=User.query.filter_by(username=session['username']).first()
            
            newpost=Blog(title,entry, owner=owner)
            db.session.add(newpost)
            db.session.commit()

            entry_id = str(newpost.id)
            return redirect('./blog?id=' + entry_id)

    return render_template('newpost.html') 

#displays a list of all blogz users with links to their individual pages
@app.route('/')
def index ():
    #get the username of all the objects of the User class 
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()

