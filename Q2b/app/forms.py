from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, SelectMultipleField, FieldList, BooleanField, FormField
from wtforms.validators import InputRequired, Email, Length, InputRequired, URL

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=64)])
    name = StringField('Name', validators=[InputRequired(), Length(max=60)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=64)])

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    genres = SelectMultipleField('Choose Multiple Genres (Hold Ctrl to click more than 1 Genre):', choices=[
        ("Animals", "Animals"), ("Business", "Business"), ("Comics", "Comics"), ("Communication", "Communication"),
        ("Dark Academia", "Dark Academia"), ("Emotion", "Emotion"), ("Fantasy", "Fantasy"), ("Fiction", "Fiction"),
        ("Friendship", "Friendship"), ("Graphic Novels", "Graphic Novels"), ("Grief", "Grief"),
        ("Historical Fiction", "Historical Fiction"), ("Indigenous", "Indigenous"), ("Inspirational", "Inspirational"),
        ("Magic", "Magic"), ("Mental Health", "Mental Health"), ("Nonfiction", "Nonfiction"),
        ("Personal Development", "Personal Development"), ("Philosophy", "Philosophy"), ("Picture Books", "Picture Books"),
        ("Poetry", "Poetry"), ("Productivity", "Productivity"), ("Psychology", "Psychology"), ("Romance", "Romance"),
        ("School", "School"), ("Self Help", "Self Help")], coerce=str)
    category = SelectField('Choose a Category:', choices=[('Children', 'Children'), ('Teens', 'Teens'), ('Adult', 'Adult')])
    cover_url = StringField('URL for Cover:', validators=[URL()])
    description = TextAreaField('Description:', validators=[InputRequired()])
    author_1 = StringField('Author 1', validators=[InputRequired()])
    illustrator_1 = BooleanField('Illustrator')
    author_2 = StringField('Author 2')
    illustrator_2 = BooleanField('Illustrator')
    author_3 = StringField('Author 3')
    illustrator_3 = BooleanField('Illustrator')
    author_4 = StringField('Author 4')
    illustrator_4 = BooleanField('Illustrator')
    author_5 = StringField('Author 5')
    illustrator_5 = BooleanField('Illustrator')
    pages = IntegerField('Number of Pages:', validators=[InputRequired()])
    copies = IntegerField('Number of Copies:', validators=[InputRequired()])