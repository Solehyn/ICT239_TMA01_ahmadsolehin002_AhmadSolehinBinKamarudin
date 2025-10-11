from flask import Flask, render_template, request
from books import all_books

app = Flask(__name__)

@app.route("/")
@app.route("/booktitles")
def booktitles():

    selected_category = request.args.get('category', 'All')

    if selected_category == 'All':
        filtered_books = all_books
    else:
        filtered_books = [book for book in all_books if book.get('category') == selected_category]

    sorted_books = sorted(filtered_books, key=lambda book: book['title'])
    
    return render_template("booktitles.html", books=sorted_books, current_category=selected_category)

@app.route("/bookdetails/<title>")
def bookdetails(title):

    selected_book = next((book for book in all_books if book['title'] == title), None)
    
    return render_template("bookdetails.html", book=selected_book)
