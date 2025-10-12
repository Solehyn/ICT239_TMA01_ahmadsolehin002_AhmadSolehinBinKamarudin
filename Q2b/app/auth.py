from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import RegisterForm, LoginForm, AddBookForm
from app.user import User
from app.model import Book
from app.loan import Loan
from random import randint
from datetime import datetime, timedelta

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
def make_loan(title):
    book = Book.get_book_by_title(title)
    if not current_user.is_authenticated:
        flash(f"Please login or register first to get an account", category="login")
        return redirect(url_for("auth.login"))
    if not book:
        flash(f"Book '{title}' not found.", category="danger")
        return redirect(url_for("booktitles"))

    existing_loan = Loan.get_active_loan(current_user, book)
    if existing_loan:
        flash(f"You already have an active loan for '{book.title}'.", category="make_loan")
        return redirect(url_for("booktitles"))

    if book.available <= 0:
        flash(f"No copies available for '{book.title}'.", category="make_loan")
        return redirect(url_for("booktitles"))

    days_ago = randint(10, 20)
    borrow_date = datetime.now() - timedelta(days=days_ago)

    Loan.create_loan(user=current_user, book=book)
    loan = Loan.get_active_loan(current_user, book)
    loan.borrow_date = borrow_date
    loan.save()

    flash(f"You have successfully made a loan for '{book.title}'!", category="make_loan")
    return redirect(url_for("booktitles"))

@auth.route("/loans", methods=["GET"])
@login_required
def view_loans():

    loans = Loan.get_user_loans(current_user)

    for loan in loans:
        loan.due_date = loan.borrow_date + timedelta(days=14)
        loan.can_return = (loan.return_date is None)
        loan.can_renew = (loan.return_date is None and loan.renew_count < 2 and loan.due_date >= datetime.now())
        loan.can_delete = (loan.return_date is not None)

    return render_template("loans.html", loans=loans)

@auth.route("/renew_loan/<loan_id>", methods=["GET"])
@login_required
def renew_loan(loan_id):
    loan = Loan.get_loan_by_id(loan_id)
    if not loan or loan.user != current_user:
        flash("Invalid loan.", "danger")
        return redirect(url_for("auth.view_loans"))
    if loan.renew_count >= 2:
        flash(f"Cannot renew '{loan.book.title}' again.", category="renew_loan")
        return redirect(url_for("auth.view_loans"))
    if loan.return_date:
        flash(f"Cannot renew '{loan.book.title}' because it has been returned.", category="renew_loan")
        return redirect(url_for("auth.view_loans"))

    rand_days = randint(10, 20)
    new_borrow_date = min(loan.borrow_date + timedelta(days=rand_days), datetime.now())
    loan.borrow_date = new_borrow_date
    loan.renew_count += 1
    loan.save()

    flash(f"'{loan.book.title}' has been renewed.", category="renew_loan")
    return redirect(url_for("auth.view_loans"))

@auth.route("/return_loan/<loan_id>", methods=["GET"])
@login_required
def return_loan(loan_id):
    loan = Loan.get_loan_by_id(loan_id)
    if not loan or loan.user != current_user:
        flash("Invalid loan.", "danger")
        return redirect(url_for("auth.view_loans"))

    if loan.return_date:
        flash(f"'{loan.book.title}' has already been returned.", category="return_loan")
        return redirect(url_for("auth.view_loans"))

    rand_days = randint(10, 20)
    proposed_return_date = loan.borrow_date + timedelta(days=rand_days)
    loan.return_date = min(proposed_return_date, datetime.now())
    loan.save()

    loan.book.available += 1
    loan.book.save()

    flash(f"'{loan.book.title}' has been returned successfully.", category="return_loan")
    return redirect(url_for("auth.view_loans"))

@auth.route("/delete_loan/<loan_id>", methods=["GET"])
@login_required
def delete_loan(loan_id):
    loan = Loan.get_loan_by_id(loan_id)
    if not loan or loan.user != current_user:
        flash("Invalid loan.", "danger")
        return redirect(url_for("auth.view_loans"))

    if not loan.return_date:
        flash("Only returned loans can be deleted.", category="delete_loan")
        return redirect(url_for("auth.view_loans"))

    loan.delete()
    flash(f"'{loan.book.title}' has been deleted.", category="delete_loan")
    return redirect(url_for("auth.view_loans"))