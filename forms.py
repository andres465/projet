# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Adresse Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), EqualTo('confirm', message='Les mots de passe doivent correspondre')])
    confirm = PasswordField('Répétez le mot de passe')
    full_name = StringField('Nom complet', validators=[DataRequired()])

class EventForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_datetime = DateTimeField('Date et Heure de Début', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeField('Date et Heure de Fin', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Lieu')
    organizer = StringField('Organisateur')
    tags = StringField('Tags')
