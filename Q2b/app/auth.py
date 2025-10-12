from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms import RegisterForm, LoginForm
from app.user import User

from app.forms import AddBookForm
from app.model import Book

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
        title = form.title.data
        genres = form.genres.data
        category = form.category.data
        cover_url = form.cover_url.data
        description = form.description.data
        if description:
            description_list = [p.strip() for p in description.split("\r\n\r\n") if p.strip()]
        else:
            description_list = []
        authors = []

        for i in range(1, 6):
            author_field = getattr(form, f'author_{i}')
            illustrator_field = getattr(form, f'illustrator_{i}')
            
            author_name = author_field.data
            if author_name:
                if illustrator_field.data:
                    author_name = f"{author_name} (Illustrator)"
                authors.append(author_name)

        pages = form.pages.data
        copies = form.copies.data

        new_book = Book(
            title=title,
            genres=genres,
            category=category,
            url=cover_url,
            description=description_list,
            authors=authors,
            pages=pages,
            available=copies,
            copies=copies
        )
        new_book.save()

        flash(f"Book '{title}' has been successfully added!", category="add_book")
        return render_template("add_book.html", form=form)

    return render_template("add_book.html", form=form)

@auth.route("/make_loan/<title>", methods=["GET"])
@login_required
def make_loan(title):
    book = Book.get_book_by_title(title)
    if book and book.available > 0:
        book.available -= 1
        book.save()
        flash(f"You have successfully made a loan for '{book.title}'!", category="make_loan")
    else:
        flash(f"No copies available for '{book.title}'.", category="make_loan")
    return redirect(url_for('booktitles'))
