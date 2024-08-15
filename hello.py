from flask import Flask, render_template, redirect, url_for, request, send_from_directory, abort
from functools import wraps
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from flask_ckeditor import CKEditor
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import os
from forms import *

#constants
app_key = os.environ["APP_KEY"]

#website application
app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

#database
class Base(DeclarativeBase):
    pass

app.secret_key = os.environ["secret_key"]

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_name")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

############databases
class Blogposts(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    subtitle: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author_id = relationship("Users", back_populates="posts")
    content: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    comments = relationship("Comments", back_populates="parent_post")



class Users(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    comments = relationship("Comments", back_populates="comment_author")
    posts = relationship("Blogposts", back_populates="author_id")

class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(), nullable=False)

    author: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("Users", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blogposts.id"))
    parent_post = relationship("Blogposts", back_populates="comments")


# with app.app_context():
#     db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)

###decorators
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)

@login_manager.unauthorized_handler
def unauthorized():
    a_response = "Unauthorised access request. Please login or register."
    return a_response

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


#############website links
#####home page
@app.route("/")
def main_page():
    return render_template("main_page.html")

######## other pages
@app.route("/notes")
def notes():
    return render_template("notes_page.html")


@app.route("/python")
def python_notes():
    return render_template("python_page.html")


@app.route("/visuals")
def visuals():
    return render_template("visuals_page.html")


@app.route("/html")
def html_page():
    return render_template("html_page.html")

@app.route('/posts')
def posts_page():
    all_posts = db.session.execute(db.select(Blogposts).order_by(Blogposts.date.desc())).scalars()
    return render_template("post_page.html", all_posts=all_posts, current_user=current_user)

####footer#####
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=["GET", "POST"])
@login_required
def contact():
    form = Contact_Form()
    sent_message = False
    if form.validate_on_submit():
        NAME = current_user.name
        NUMBER = request.form["phone_number"]
        MESSAGE = request.form["message"]
        EMAIL = current_user.email
        with smtplib.SMTP("smtp.gmail.com") as connection:
            my_email = os.environ.get('real_email')
            connection.starttls()
            connection.login(user=my_email, password=app_key)
            connection.sendmail(from_addr=my_email, to_addrs=my_email, msg=f"Subject: Message from website.\n\n"
                                                                           f"From: {NAME}. Email: {EMAIL} \n"
                                                                           f"Phone: {NUMBER}.\n"
                                                                           f"Message: {MESSAGE}.")
        return redirect(url_for("posts_page"))
    return render_template("contact.html", sent_message=sent_message, form=form)

############posts brain
@app.route('/posts/<posts_id>', methods=["GET", "POST"])
def posts(posts_id):
    post = db.get_or_404(Blogposts, posts_id)
    comment_form = Comment_Form()
    return render_template("post_format.html", post=post, form=comment_form, current_user=current_user)


@app.route('/create_post', methods=["GET", "POST"])
@login_required
def create():
    form = Post_form()
    if form.validate_on_submit():
        new_blog = Blogposts(
            title=request.form["title"],
            subtitle=request.form["subtitle"],
            date=date.today().strftime("%B %d, %Y"),
            author=current_user.name,
            content=request.form["content"],
            img_url=request.form["img_url"]
        )
        with app.app_context():
            db.session.add(new_blog)
            db.session.commit()
        return redirect(url_for('posts_page'))
    return render_template('create_post.html', form=form, current_user=current_user)


@app.route('/edit_post/<int:post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Blogposts, post_id)
    edit_form = Post_form(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        content=post.content,
    )
    if edit_form.validate_on_submit():
        post.title = request.form["title"]
        post.subtitle = request.form["subtitle"]
        post.img_url = request.form["img_url"]
        post.author = current_user.name
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for('posts', posts_id=post.id))
    return render_template('create_post.html', form=edit_form, current_user=current_user, editing=True)


@app.route('/delete/<int:post_id>', methods=["GET"])
@login_required
@admin_only
def delete(post_id):
    post = db.get_or_404(Blogposts, post_id)
    with app.app_context():
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('posts_page'))




###############users management
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        new_user = Users(
            email=request.form["email"],
            password=generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=8),
            name=request.form["name"],
        )
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
        login_user(new_user)
        return redirect(url_for('posts_page'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if user:
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user)
                return redirect(url_for('posts_page'))
            return render_template("login.html", form=form, password_incorrect=True)
        return render_template("login.html", form=form, user_incorrect=True)
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))


if __name__ == "__main__":
    app.run(debug=True)