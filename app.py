from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import secrets

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Clé secrète aléatoire

# Configuration de la base de données SQLite (exemple)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservation_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy(app)

# Configuration de Flask-Login
login_manager = LoginManager(app)

# Définition du modèle Utilisateur
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

# Fonction pour charger l'utilisateur à partir de son ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes et logique de l'application

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == password:
            login_user(user)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    return render_template('login.html')

# Route pour la page d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']

        # Vérification si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.', 'error')
            return redirect(url_for('register'))

        # Création d'un nouvel utilisateur
        new_user = User(username=username, password_hash=password, email=email, full_name=full_name)
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route pour la page de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('login'))

# Autres routes pour gérer les événements, réservations, etc.
# Assurez-vous d'ajouter ces routes selon vos besoins

# Exécution de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
