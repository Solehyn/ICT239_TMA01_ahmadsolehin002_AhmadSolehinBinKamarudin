from flask import render_template, request
from app.model import Book
from app import app, db

Book.initialize_collection()

@app.route("/")
@app.route("/booktitles")
def booktitles():

    selected_category = request.args.get('category', 'All')

    if selected_category == 'All':
        filtered_books = Book.objects()  
    else:
        filtered_books = Book.objects(category=selected_category)

    sorted_books = list(filtered_books.order_by('+title'))
    
    return render_template("booktitles.html", books=sorted_books, current_category=selected_category)

@app.route("/bookdetails/<title>")
def bookdetails(title):

    selected_book = Book.objects(title=title).first() 
    
    return render_template("bookdetails.html", book=selected_book)

