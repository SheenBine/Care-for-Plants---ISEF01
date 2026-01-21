import os
from flask import Flask, request, render_template, redirect, url_for
from models import db, User

# Flask-App erstellen
app = Flask(__name__)

# Absoluter Pfad zum database-Ordner außerhalb von backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'database.db')

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
    Zeigt die index.html an.
    '''
    return render_template('index.html')


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
                return f"Registrierung erfolgreich! Willkommen {username}!"
            except Exception as e:
                db.session.rollback()
                return f"Fehler bei der Registrierung: {str(e)}"

        # Login
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return f"Login erfolgreich! Willkommen {username}!"
            else:
                return "Login fehlgeschlagen!"

    # Standardmäßig GET, um Login/Registrierung zu zeigen
    return render_template('login.html')


# App starten
if __name__ == '__main__':
    app.run(debug=True)
