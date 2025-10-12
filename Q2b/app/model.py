from app import db
from app.books import all_books

class Book(db.Document):
    """
    MongoEngine Document definition for the Book collection.
    It defines the structure of the Book documents in MongoDB, 
    matching the provided data structure and class diagram.
    """
    meta = {'collection': 'books'}

    genres = db.ListField(db.StringField(), required=True)
    title = db.StringField(required=True, unique=True)
    category = db.StringField(required=True)
    url = db.StringField()
    description = db.ListField(db.StringField())
    authors = db.ListField(db.StringField(), required=True)
    pages = db.IntField()
    available = db.IntField()
    copies = db.IntField(default=0)

    @staticmethod
    def get_book_by_title(title):
        """
        Static method to retrieve a book by its title.
        """
        return Book.objects(title=title).first()
    
    @staticmethod
    def get_all_books():
        """
        Static method to retrieve all books.
        """
        return Book.objects()
    
    @staticmethod
    def save_book(genres, title, category, url, description, authors, pages, available, copies):
        """
        Static method to save a new book to the database.
        """
        book = Book(genres=genres, title=title, category=category, url=url, description=description, authors=authors, pages=pages, available=available, copies=copies)
        book.save()
        return book

    @classmethod
    def initialize_collection(cls):
        """
        Checks if the Book collection is empty. If so, it reads 
        data from all_books and inserts it into MongoDB.
        """
        if cls.objects.count() == 0:
            for book_data in all_books:
                cls.save_book(genres=book_data['genres'], title=book_data['title'], category=book_data['category'], url=book_data['url'], description=book_data['description'], authors=book_data['authors'], pages=book_data['pages'], available=book_data['available'], copies=book_data['copies'])
    
    def save(self, *args, **kwargs):
        if self.available is None:
            self.available = self.copies
        return super(Book, self).save(*args, **kwargs)

    def borrow(self):

        if self.available > 0:
            self.available -= 1
            self.save()
            return True
        else:
            return False

    def return_book(self):

        if self.available < self.copies:
            self.available += 1
            self.save()
            return True
        else:
            return False 