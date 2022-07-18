import os

from flask import Flask, render_template, redirect, url_for, flash, abort, session, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm, DateForm
from flask_gravatar import Gravatar
import smtplib
from sqlalchemy import and_, desc, asc
from flask_compress import Compress

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "8BYkEfBA6O6donzWlSihBXox7C0sKR6b")
ckeditor = CKEditor(app)
Bootstrap(app)
Compress(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

MY_EMAIL = "enter_your_email"
EMAIL_PASSWORD = "enter_your_pass"



##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///juntos.db")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def before_request():
    #if app.env == "development":
     #    return
    #if request.is_secure:
     #    return
    #url = request.url.replace("http://", "https://", 1)
    #code = 301
    #return redirect(url, code=code)

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(400), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
    hour = db.Column(db.String(250))
    name = db.Column(db.String(250))
    email = db.Column(db.String(250))
    phone = db.Column(db.String(100))

db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.order_by(desc(BlogPost.id))
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("El email ya se encuentra registrado, en su lugar iniciar sesión!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("El email no existe, por favor, intente nuevamente.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Contraseña incorrecta, por favor, intente nuevamente.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Necesitás estar logueado para comentar el post.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/why-counseling")
def why_counseling():
    return render_template("why-counseling.html", current_user=current_user)


@app.route("/modalidad")
def modalidad():
    return render_template("modalidad.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:Nuevo Mensaje\n\nNombre: {name}\nEmail: {email}\nTelefono: {phone}\nMensaje:{message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, EMAIL_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL, msg=email_message)


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    form = DateForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Necesitas estar logueado para agendar una cita.")
            return redirect(url_for("login"))

        if Appointment.query.filter(and_(
                Appointment.date.like(form.date.data.strftime('%Y-%m-%d')),
                Appointment.hour.like(form.hour.data.strftime('%H:%M'))
        )
        ).first():
            flash("La fecha ya fue seleccionada")
            return redirect(url_for('appointment'))
        data = Appointment(
            date=str(form.date.data.strftime('%Y-%m-%d')),
            hour=str(form.hour.data.strftime('%H:%M')),
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data

        )
        send_email_appointment(form.date.data, form.hour.data, form.name.data, form.email.data, form.phone.data)
        db.session.add(data)
        db.session.commit()
        return render_template("appointment.html", form=form, day_sent=True)
    return render_template("appointment.html", form=form, current_user=current_user, day_sent=False)


def send_email_appointment(date, hour, name, email, phone):
    email_message = f"Subject: Turno confirmado: \n\nNombre: {name} \nTeléfono: {phone} \nEmail: {email} \nCuándo: {date}\nHorario:{hour}\n\n\n" \
                    f"El link de ingreso será enviado previo al encuentro.\n" \
                    f"Si necesitás cancelar la cita, deberás hacerlo con 24 horas de anticipación a través de este mail.\n" \
                    f"¡Gracias por elegirnos!\n Caminemos Juntos Counseling\n Todos los derechos reservados."
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, EMAIL_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=email, msg=email_message.encode('utf-8'))
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL, msg=email_message.encode('utf-8'))


@app.route('/get-all-appointments')
@admin_only
def get_all_appointments():
    all_dates = Appointment.query.order_by(desc(Appointment.date))
    return render_template("get-all-appointments.html", all_dates=all_dates, current_user=current_user)

@app.route("/new-post", methods=["GET", "POST"])
@admin_only
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

    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/delete_date/<int:date_id>")
@admin_only
def delete_date(date_id):
    date_to_delete = Appointment.query.get(date_id)
    db.session.delete(date_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_appointments'))

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=False)
