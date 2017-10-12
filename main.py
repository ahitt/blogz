from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key= True) 
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)
    
    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
 

#displays all the blog posts
@app.route('/blog', methods = ['GET'])
def display_posts():
    if len(request.args) != 0:
        entry_id = request.args.get('id')
        entry = Blog.query.get(entry_id)

        return render_template('entry.html', entry=entry)

    posts = Blog.query.order_by(Blog.pub_date)
    return render_template('blog.html', posts=posts)

#displays new blog posts
@app.route('/newpost', methods =['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['entry']

        if title == "" or entry == "":
            if title == "":
                title_error = "Enter a title"
            if entry == "":
                entry = "Enter a body for the post"
            return render_template('newpost.html', title=title, entry=entry, entry_error=entry_error, title_error=title_error)
        else:
            newpost=Blog(title,entry)
            db.session.add(newpost)
            db.session.commit()
            entry_id = str(newpost.id)
            return redirect('/blog')

    return render_template('newpost.html') 

@app.route('/')
def index ():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()

