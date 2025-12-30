from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from typing import List
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import forms from the forms.py.
from forms import CreatePostForm, RegistrationForm, LoginForm, CommentForm, ContactForm
import os
from dotenv import load_dotenv
# Import email_sender module.
from email_sender import SENDMAIL

#Load environmental variables
load_dotenv()



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("app_secret")
ckeditor = CKEditor(app)
Bootstrap5(app)


# TODO: Configure Flask-Login.
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)


def search_user_by_email(email):
    '''Search database of users by email, returns user or None'''
    try:
        user = db.one_or_404( db.select(User).filter_by(email=email),
    description=(f"No '{email}' email in user database."))
    except Exception as e:
        user = None
        print(e)
    else:
        pass
    finally:
        return user

# CREATE DATABASE.
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(key="DB_URI", default="sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES.
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    # Linking it to users table.
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    #Linking to Comment table.
    post_comments : Mapped[List["Comment"]] = relationship(back_populates="parent_post")

# TODO: Create a User table for all your registered users. 
class User(db.Model,UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    user_name: Mapped[str] = mapped_column(String,unique=True)
    email: Mapped[str] = mapped_column(String,unique=True)
    password: Mapped[str]

    #relation linking it to blog_post table.
    posts: Mapped[List["BlogPost"]] = relationship(back_populates="author")

    #relation link to comments.
    comment: Mapped[List["Comment"]] = relationship(back_populates="comment_author")
    

# TODO: Create a comments table.
class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    text: Mapped[str] = mapped_column(Text,unique=False)

    # Linking to User.
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment_author: Mapped["User"] = relationship(back_populates="comment")

    # Linking to block posts.
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    parent_post : Mapped["BlogPost"] = relationship(back_populates="post_comments")

with app.app_context():
    db.create_all()


# TODO: Create admin only decorator, deny permission.

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('login'))
        #If id is not 1 then return abort with 403 error.
        if current_user.is_anonymous:
            abort(403)
        if current_user.id != 1:
            abort(403)
        else: 
            return f(*args, **kwargs)
    return decorated_function



# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.user_name = form.user_name.data
        user.email = form.email.data
        password = form.password.data
        hashed_password = generate_password_hash(password=password,method="pbkdf2:sha256:600000",salt_length=12)
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods = ['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = search_user_by_email(email)
        # Check user and password.
        if user is None:
            flash("Incorrect username, Please enter correct username")
            print('incorrect username')
            return redirect(url_for('login'))
        elif check_password_hash(password = password, pwhash = user.password):
            login_user(user)
            print("success Logged in")
            return redirect(url_for('get_all_posts'))
        else:
            flash("Incorrect password, Please enter correct password")
            print("incorrect password")

    return render_template("login.html",form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts.
@app.route("/post/<int:post_id>", methods = ["GET","POST"])
def show_post(post_id):
    try:
        requested_post = db.get_or_404(BlogPost, post_id)
    except Exception as e:
        print("Nothing in database")
        requested_post = None

    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash('You need to log in to add comment. Register if you do not have an account')
            return redirect(url_for('login'))
        new_comment = Comment()
        new_comment.author_id = current_user.id
        new_comment.text = form.comment.data
        new_comment.post_id = post_id
        db.session.add(new_comment)
        db.session.commit()
    
    for item in requested_post.post_comments:
        print(dir(item.author_id))

    return render_template("post.html", post=requested_post, form=form, comments = requested_post.post_comments)


# TODO: Use a decorator so only an admin user can create a new post.
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post.
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post.
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")

#TODO: Fix the contact me page.
@app.route("/contact", methods =["GET","POST"])
def contact():
    contact_form = ContactForm()

    if contact_form.validate_on_submit():
        # Contact form Data
        name = contact_form.name.data
        company = contact_form.company.data
        email = contact_form.email.data
        phone_number = contact_form.phone_number.data
        message = contact_form.message.data

        # Format and send email.
        # Initializing email_sender class object.
        mail = SENDMAIL()
        subject = 'Contact from Blog'
        body = f'{message}\n\nKind Regards\nname: {name} \nCompany {company} \nnumber :{phone_number}'

        # Gmail authentication data.
        sender = os.getenv('sender_email')
        reciever_email = os.getenv('reciever_email')
        gmail_app_password = os.getenv('gmail_app_password')

        # Sending the email.
        try:
            mail.send_email(sender,reciever_email,gmail_app_password,subject,body)
            flash('Message sent')
        except NameError as e:
            print(e)
        except Exception as e:
            print(e)
        else:
            print("No exceptions caught")

    return render_template("contact.html",form=contact_form)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
