from app import db
from datetime import datetime, timedelta
from app.model import Book
from app.user import User

class Loan(db.Document):
    meta = {'collection': 'loans'}

    user = db.ReferenceField(User, required=True)
    book = db.ReferenceField(Book, required=True)
    borrow_date = db.DateTimeField(default=datetime.now)
    return_date = db.DateTimeField(null=True) 
    renew_count = db.IntField(default=0)

    ## Create a loan
    @staticmethod
    def create_loan(user, book):
        """
        Create a loan for a user if:
        1. The user does not have an unreturned loan for the same book.
        2. The book has available copies.
        Updates the book's available count if successful.
        Returns the Loan instance if created, or None if failed.
        """
        existing_loan = Loan.objects(user=user, book=book, return_date=None).first()
        if existing_loan:
            return None

        if book.available <= 0:
            return None 

        new_loan = Loan(user=user, book=book, borrow_date=datetime.now)
        new_loan.save()

        book.available -= 1
        book.save()

        return new_loan

    ## Retrieve loans
    @staticmethod
    def get_user_loans(user):
        """Return all loans (active and returned) for a user."""
        return Loan.objects(user=user).order_by('-borrow_date')

    @staticmethod
    def get_active_loan(user, book):
        """Return active loan for this user and book, or None."""
        return Loan.objects(user=user, book=book, return_date=None).first()

    @staticmethod
    def get_loan_by_id(loan_id):
        """Retrieve a loan by its MongoEngine id."""
        return Loan.objects(pk=loan_id).first()

    ## Update loans
    def renew(self):
        """
        Renew an active loan.
        Increments renew_count and updates borrow_date.
        """
        if self.return_date is not None:
            return False
        self.renew_count += 1
        self.borrow_date = datetime.now
        self.save()
        return True

    def return_loan(self):
        """
        Mark loan as returned and update book's available count.
        """
        if self.return_date is not None:
            return False
        self.return_date = datetime.now
        self.save()

        self.book.available += 1
        self.book.save()
        return True

    ## Delete loan
    def delete_loan(self):
        """
        Delete the returned loan from the database.
        """
        if self.return_date is None:
            return False
        self.delete()
        return True