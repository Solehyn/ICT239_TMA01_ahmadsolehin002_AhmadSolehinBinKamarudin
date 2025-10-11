from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

db = MongoEngine()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret' 
    app.config['MONGODB_SETTINGS'] = {
        'db': 'books_db',
        'host': 'localhost',
        'port': 27017,
    }

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.user import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.objects(pk=user_id).first()

    return app

app = create_app()