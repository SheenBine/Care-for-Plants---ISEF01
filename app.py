import os
from flask import Flask, request, render_template, redirect, url_for, session
from models import db, User

# localhost:5000/ http://localhost:5000/
# Flask-App erstellen
app = Flask(__name__)

# Absoluter Pfad zum Projektordner und zur SQLite-Datei im lokalen database-Ordner
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')

# SQLAlchemy-Datenbank-URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
# Secret Key für Session-Cookie (für diesen Zweck einfach gehalten)
app.config['SECRET_KEY'] = 'thisisasecretkey'

# Datenbank mit Flask verbinden
db.init_app(app)

# Tabellen in der Datenbank anlegen, falls noch nicht vorhanden
with app.app_context():
    db.create_all()

# Prüft, ob der Testuser existiert, legt ihn sonst an
    if not User.query.filter_by(username="testuser").first():
        try:
            testuser = User(username="testuser")
            testuser.set_password("1234") 
            db.session.add(testuser)
            db.session.commit()
            print("Testuser 'testuser' automatisch angelegt")
        except Exception as e:
            db.session.rollback()
            print(f"Fehler beim Anlegen des Testusers: {e}")

# Routen
@app.route('/')
def home():
    '''
    Startseite der App.
    Prüft, ob ein User eingeloggt ist.
    Falls nicht, wird auf die Login-Seite weitergeleitet.
    '''
    # Prüfen, ob ein User eingeloggt ist
    if 'username' not in session:
        # Kein User eingeloggt -> auf Login weiterleiten
        return redirect(url_for('auth'))
    
    # User ist eingeloggt -> index.html anzeigen
    # Optional: Username an Template übergeben
    return render_template('index.html', username=session['username'])


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    '''
    Login und Registrierung auf einer Seite.
    - GET: zeigt login.html
    - POST: verarbeitet Formular mit 'login' oder 'register'
    '''
    if request.method == 'POST':
        action = request.form.get('action')  # "login" oder "register"
        username = request.form['username']
        password = request.form['password']

        # Registrierung
        if action == 'register':
            if User.query.filter_by(username=username).first():
                return "Benutzer existiert bereits!"
            try:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                # Nach erfolgreicher Registrierung direkt einloggen
                session['username'] = username
                session['user_id'] = user.id
                return redirect(url_for('home'))
            except Exception as e:
                db.session.rollback()
                return f"Fehler bei der Registrierung: {str(e)}"

        # Login
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                # Session erstellen und Username speichern
                session['username'] = username
                session['user_id'] = user.id
                # Auf die Startseite weiterleiten
                return redirect(url_for('home'))
            else:
                return "Login fehlgeschlagen!"

    # Standardmäßig GET, um Login/Registrierung zu zeigen
    return render_template('login.html')


@app.route('/logout')
def logout():
    '''
    Logout-Route.
    Löscht die Session und leitet auf die Login-Seite weiter.
    '''
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('auth'))


# App starten
if __name__ == '__main__':
    app.run(debug=True)
