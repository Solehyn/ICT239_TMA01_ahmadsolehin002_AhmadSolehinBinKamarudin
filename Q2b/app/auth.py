from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms import RegisterForm, LoginForm
from app.user import User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("booktitles"))

    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        if User.by_email(form.email.data):
            form.email.errors.append("User already exists.")
        else:
            User(email=form.email.data,
                 password=generate_password_hash(form.password.data),
                 name=form.name.data,
                 is_admin=False).save()
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("booktitles"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.by_email(form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("booktitles"))
        else:
            form.password.errors.append("Invalid email or password.")
    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("booktitles"))