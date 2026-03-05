import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from models import db, User, Location, Plant

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

def require_login():
    '''
    Prüft, ob User eingeloggt. Wenn nicht: JSON-Fehlermeldung
    '''
    user_id = session.get('user_id')
    if not user_id:
        return None, (jsonify({"error": "Nicht eingeloggt"}), 401)
    return user_id, None

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


@app.route('/api/wishlist', methods=['GET'])
def api_list_wishlist():
    '''
    Wunschliste anzeigen. Also Plants mit is_purchased = False (nur eigene)
    '''
    user_id, err = require_login()
    if err:
        return err

    plants = Plant.query.filter_by(user_id=user_id, is_purchased=False).order_by(Plant.created_at.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "botanical_name": p.botanical_name,
            "light_requirement": p.light_requirement,
            "water_requirement": p.water_requirement,
            "temperature_min": p.temperature_min,
            "temperature_max": p.temperature_max,
            "humidity_requirement": p.humidity_requirement,
            "soil_type": p.soil_type,
            "height_min": p.height_min,
            "height_max": p.height_max,
            "poisonous": bool(p.poisonous),
            "flowering_season_start": p.flowering_season_start,
            "flowering_season_end": p.flowering_season_end,
            "flower_color": p.flower_color,
            "notes": p.notes,
            "created_at": str(p.created_at)
        }
        for p in plants
    ]), 200


@app.route('/api/wishlist', methods=['POST'])
def api_add_wishlist_item():
    '''
    Pflanze zur Wunschliste hinzufügen
    '''
    user_id, err = require_login()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Bitte geben Sie einen Namen ein."}), 400

    try:
        plant = Plant(
            user_id=user_id,
            name=name,
            botanical_name=data.get("botanical_name"),

            light_requirement=data.get("light_requirement"),
            water_requirement=data.get("water_requirement"),
            temperature_min=data.get("temperature_min"),
            temperature_max=data.get("temperature_max"),
            humidity_requirement=data.get("humidity_requirement"),
            soil_type=data.get("soil_type"),

            height_min=data.get("height_min"),
            height_max=data.get("height_max"),
            poisonous=bool(data.get("poisonous")) if data.get("poisonous") is not None else False,
            flowering_season_start=data.get("flowering_season_start"),
            flowering_season_end=data.get("flowering_season_end"),
            flower_color=data.get("flower_color"),

            notes=data.get("notes"),

            # Wunschliste = nicht gekauft
            is_purchased=False,

            location_id=None
        )

        db.session.add(plant)
        db.session.commit()

        return jsonify({"id": plant.id, "message": "Zur Wunschliste hinzugefügt"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Hinzufügen: {str(e)}"}), 400


@app.route('/api/wishlist/<int:plant_id>', methods=['DELETE'])
def api_remove_wishlist_item(plant_id):
    '''
    Pflanze von der Wunschliste entfernen
    '''
    user_id, err = require_login()
    if err:
        return err

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id, is_purchased=False).first()
    if not plant:
        return jsonify({"error": "Wunschlisten-Eintrag nicht gefunden"}), 404

    try:
        db.session.delete(plant)
        db.session.commit()
        return jsonify({"message": "Von Wunschliste entfernt"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Entfernen: {str(e)}"}), 400


@app.route('/api/locations', methods=['GET'])
def api_list_locations():
    '''
    Standorte anzeigen
    '''
    user_id, err = require_login()
    if err:
        return err

    locations = Location.query.filter_by(user_id=user_id).order_by(Location.created_at.desc()).all()

    return jsonify([
        {
            "id": loc.id,
            "name": loc.name,
            "lighting_condition": loc.lighting_condition,
            "temperature": loc.temperature,
            "humidity": loc.humidity,
            "description": loc.description,
            "created_at": str(loc.created_at)
        }
        for loc in locations
    ]), 200


@app.route('/api/locations', methods=['POST'])
def api_create_location():
    '''
    Standort anlegen
    '''
    user_id, err = require_login()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Bitte Name eingeben"}), 400

    try:
        loc = Location(
            user_id=user_id,
            name=name,
            lighting_condition=data.get("lighting_condition"),
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            description=data.get("description")
        )
        db.session.add(loc)
        db.session.commit()

        return jsonify({"id": loc.id, "message": "Standort erstellt"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Erstellen: {str(e)}"}), 400


@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
def api_delete_location(location_id):
    '''
    Standort löschen
    '''
    user_id, err = require_login()
    if err:
        return err

    loc = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not loc:
        return jsonify({"error": "Standort nicht gefunden"}), 404

    try:
        db.session.delete(loc)
        db.session.commit()
        return jsonify({"message": "Standort gelöscht"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Löschen: {str(e)}"}), 400

# App starten
if __name__ == '__main__':
    app.run(debug=True)
