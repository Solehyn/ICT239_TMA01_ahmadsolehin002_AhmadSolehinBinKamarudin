from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms import RegisterForm, LoginForm
from app.user import User

from app.forms import AddBookForm
from app.model import Book

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField

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

@auth.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = AddBookForm()

    if form.validate_on_submit():
        # Gather form data
        title = form.title.data
        genres = form.genres.data
        category = form.category.data
        cover_url = form.cover_url.data
        description = form.description.data
        if description:
            # Split on double line breaks (paragraphs)
            description_list = [p.strip() for p in description.split("\r\n\r\n") if p.strip()]
        else:
            description_list = []
        authors = []

        # Process each author field
        for i in range(1, 6):
            author_field = getattr(form, f'author_{i}')
            illustrator_field = getattr(form, f'illustrator_{i}')
            
            author_name = author_field.data
            if author_name:
                # If Illustrator checkbox is ticked, append "(Illustrator)" to the name
                if illustrator_field.data:
                    author_name = f"{author_name} (Illustrator)"
                authors.append(author_name)

        pages = form.pages.data
        copies = form.copies.data

        # Save to the database (Book document)
        new_book = Book(
            title=title,
            genres=genres,
            category=category,
            url=cover_url,
            description=description_list,
            authors=authors,  # List of authors (including illustrator status)
            pages=pages,
            available=copies,
            copies=copies
        )
        new_book.save()

        flash(f"Book '{title}' has been successfully added!", "success")
        return render_template("add_book.html", form=form)

    return render_template("add_book.html", form=form)