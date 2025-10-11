# app/user_model.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db

class User(UserMixin, db.Document):
    meta = {'collection': 'users'}
    email = db.StringField(required=True, unique=True, max_length=100)
    password = db.StringField(required=True)  # store hash
    name = db.StringField(required=True, max_length=60)
    avatar = db.StringField(default="")
    is_admin = db.BooleanField(default=False)

    def get_id(self):
        # MongoEngine pk is ObjectId; Flask-Login stores it as string
        return str(self.pk)

    @staticmethod
    def by_email(email):
        return User.objects(email=email).first()

    @staticmethod
    def seed_defaults():
        """Create the two required users if missing."""
        defaults = [
            dict(email="admin@lib.sg", password="12345", name="Admin", avatar="admin.jpeg", is_admin=True),
            dict(email="poh@lib.sg",   password="12345", name="Peter Oh", avatar="", is_admin=False),
        ]
        for u in defaults:
            if not User.by_email(u["email"]):
                User(email=u["email"],
                     password=generate_password_hash(u["password"]),
                     name=u["name"],
                     avatar=u.get("avatar", ""),
                     is_admin=u["is_admin"]).save()