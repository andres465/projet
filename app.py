from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:180113@localhost/gdd_prod2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Definir tus modelos de datos
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    organizer = db.Column(db.String(100))
    tags = db.Column(db.String(100))


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')

    user = db.relationship('User', backref='bookings')
    event = db.relationship('Event', backref='bookings')


# Rutas y Vistas

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('La connexion a échoué. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe.', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Le nom d\'utilisateur existe déjà. Veuillez en choisir un différent.', 'error')
        else:
            new_user = User(username=username, email=email, full_name=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Inscription réussie. Veuillez vous connecter.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    bookings = current_user.bookings
    return render_template('dashboard.html', bookings=bookings)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)


@app.route('/events')
def event_list():
    events = Event.query.all()
    return render_template('event_list.html', events=events)


# Agregar evento
@app.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')
        location = request.form['location']
        organizer = request.form['organizer']
        tags = request.form['tags']

        new_event = Event(title=title, description=description, start_datetime=start_datetime,
                          end_datetime=end_datetime, location=location, organizer=organizer, tags=tags)

        db.session.add(new_event)
        db.session.commit()

        flash('Événement ajouté avec succès.', 'success')
        return redirect(url_for('event_list'))

    return render_template('add_event.html')


# Modifier événement
@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
        event.end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')
        event.location = request.form['location']
        event.organizer = request.form['organizer']
        event.tags = request.form['tags']

        db.session.commit()

        flash('Événement modifié avec succès.', 'success')
        return redirect(url_for('event_details', event_id=event.id))

    return render_template('edit_event.html', event=event)


# Formulaire de réservation
@app.route('/event/<int:event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        booking = Booking(user_id=current_user.id, event_id=event.id, booking_time=datetime.now())
        db.session.add(booking)
        db.session.commit()

        flash('Réservation effectuée avec succès.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('booking_form.html', event=event)


# Modifier le profil
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']

        db.session.commit()

        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html')


# Modifier le mot de passe
@app.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        if current_user.check_password(old_password):
            current_user.set_password(new_password)
            db.session.commit()
            flash('Mot de passe changé avec succès.', 'success')
        else:
            flash('Mot de passe actuel incorrect. Veuillez réessayer.', 'error')

    return render_template('change_password.html')


# Statut des réservations
@app.route('/event/<int:event_id>/status')
@login_required
def booking_status(event_id):
    event = Event.query.get_or_404(event_id)
    bookings = Booking.query.filter_by(event_id=event.id).all()
    return render_template('status.html', event=event, bookings=bookings)


if __name__ == '__main__':
    app.run(debug=True)
