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

# Validierung der Enum-Felder

ALLOWED_LIGHT = {"schatten", "halbschatten", "sonnig"}
ALLOWED_TEMP = {"kalt", "normal", "warm"}
ALLOWED_HUMIDITY = {"trocken", "normal", "feucht"}
ALLOWED_WATER = {"wenig", "mittel", "viel"}

def validate_enum(field_name, value, allowed_values):
    '''
    Prüft ob ein Wert in einer erlaubten Menge liegt
    - None oder "" wird als "nicht gesetzt" akzeptiert
    '''
    if value is None:
        return True, None

    # Falls Frontend mal "" schickt, behandeln wir es als None
    if isinstance(value, str) and value.strip() == "":
        return True, None

    if value not in allowed_values:
        return False, (jsonify({
            "error": f"Ungültiger Wert für {field_name}: '{value}'",
            "allowed": sorted(list(allowed_values))
        }), 400)

    return True, None

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


@app.route('/wishlist', methods=['GET'])
def list_wishlist():
    '''
    Wunschliste anzeigen. Also Plants mit is_purchased = False
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


@app.route('/wishlist', methods=['POST'])
def add_wishlist_item():
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


@app.route('/wishlist/<int:plant_id>', methods=['DELETE'])
def remove_wishlist_item(plant_id):
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


@app.route('/locations', methods=['GET'])
def list_locations():
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


@app.route('/locations', methods=['POST'])
def create_location():
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

    ok, err = validate_enum("lighting_condition", data.get("lighting_condition"), ALLOWED_LIGHT)
    if not ok:
        return err

    ok, err = validate_enum("temperature", data.get("temperature"), ALLOWED_TEMP)
    if not ok:
        return err

    ok, err = validate_enum("humidity", data.get("humidity"), ALLOWED_HUMIDITY)
    if not ok:
        return err

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


@app.route('/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
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


@app.route('/locations/<int:location_id>/plants', methods=['GET'])
def list_plants_by_location(location_id):
    '''
    Pflanzen pro Standort anzeigen
    - Standort muss dem eingeloggten User gehören.
    - Gibt Pflanzen zurück, die diesem Standort zugeordnet sind.
    '''
    user_id, err = require_login()
    if err:
        return err

    # Standort prüfen
    loc = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not loc:
        return jsonify({"error": "Standort nicht gefunden"}), 404

    plants = Plant.query.filter_by(user_id=user_id, location_id=location_id).order_by(Plant.created_at.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "botanical_name": p.botanical_name,
            "is_purchased": bool(p.is_purchased),
            "location_id": p.location_id,
            "notes": p.notes,
            "created_at": str(p.created_at)
        }
        for p in plants
    ]), 200

@app.route('/inventory', methods=['GET'])
def list_inventory():
    '''
    Bestand anzeigen
    Das sind Plants mit is_purchased = True
    '''
    user_id, err = require_login()
    if err:
        return err

    plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).order_by(Plant.created_at.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "botanical_name": p.botanical_name,
            "location_id": p.location_id,
            "notes": p.notes,
            "created_at": str(p.created_at)
        }
        for p in plants
    ]), 200


@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    '''
    Pflanze direkt in den Bestand hinzufügen
    '''
    user_id, err = require_login()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Bitte Name eingeben"}), 400

    # Standort prüfen (muss dem User gehören)
    location_id = data.get("location_id")
    if location_id is not None:
        loc = Location.query.filter_by(id=location_id, user_id=user_id).first()
        if not loc:
            return jsonify({"error": "Standort ungültig"}), 400

    try:
        plant = Plant(
            user_id=user_id,
            name=name,
            botanical_name=data.get("botanical_name"),
            notes=data.get("notes"),
            is_purchased=True,
            location_id=location_id
        )
        db.session.add(plant)
        db.session.commit()

        return jsonify({"id": plant.id, "message": "Zum Bestand hinzugefügt"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Hinzufügen: {str(e)}"}), 400


@app.route('/plants/<int:plant_id>', methods=['PATCH'])
def update_plant(plant_id):
    '''
    - Wunschliste <-> Bestand 
    - Standort zuordnen/ändern/entfernen
    - Pflanzen-Eigenschaften ergänzen/ändern

    '''
    user_id, err = require_login()
    if err:
        return err

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id).first()
    if not plant:
        return jsonify({"error": "Pflanze nicht gefunden"}), 404

    data = request.get_json(silent=True) or {}

    # Eigenschaften
    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name darf nicht leer sein"}), 400
        plant.name = name

    if "botanical_name" in data:
        plant.botanical_name = data.get("botanical_name")

    if "light_requirement" in data:
        ok, err = validate_enum("light_requirement", data.get("light_requirement"), ALLOWED_LIGHT)
        if not ok:
            return err
        plant.light_requirement = data.get("light_requirement")

    if "water_requirement" in data:
        ok, err = validate_enum("water_requirement", data.get("water_requirement"), ALLOWED_WATER)
        if not ok:
            return err
        plant.water_requirement = data.get("water_requirement")

    if "humidity_requirement" in data:
        ok, err = validate_enum("humidity_requirement", data.get("humidity_requirement"), ALLOWED_HUMIDITY)
        if not ok:
            return err
        plant.humidity_requirement = data.get("humidity_requirement")

    if "temperature_min" in data:
        try:
            temp_min = int(data.get("temperature_min"))
            plant.temperature_min = temp_min
        except (TypeError, ValueError):
            return jsonify({"error": "temperature_min muss eine Zahl sein"}), 400

    # Temperatur Maximum
    if "temperature_max" in data:
        try:
            temp_max = int(data.get("temperature_max"))
            plant.temperature_max = temp_max
        except (TypeError, ValueError):
            return jsonify({"error": "temperature_max muss eine Zahl sein"}), 400

    # Prüfen ob min <= max
    if plant.temperature_min is not None and plant.temperature_max is not None:
        if plant.temperature_min > plant.temperature_max:
            return jsonify({
                "error": "temperature_min darf nicht größer als temperature_max sein"
            }), 400
    if "soil_type" in data:
        plant.soil_type = data.get("soil_type")

    if "height_min" in data:
        plant.height_min = data.get("height_min")

    if "height_max" in data:
        plant.height_max = data.get("height_max")

    if "poisonous" in data:
        plant.poisonous = bool(data.get("poisonous"))

    if "flowering_season_start" in data:
        plant.flowering_season_start = data.get("flowering_season_start")

    if "flowering_season_end" in data:
        plant.flowering_season_end = data.get("flowering_season_end")

    if "flower_color" in data:
        plant.flower_color = data.get("flower_color")

    if "notes" in data:
        plant.notes = data.get("notes")

    # Status: Wunschliste oder Bestand
    if "is_purchased" in data:
        plant.is_purchased = bool(data.get("is_purchased"))

    # Standort zuordnen/entfernen
    if "location_id" in data:
        location_id = data.get("location_id")

        # location_id = null -> Zuordnung entfernen
        if location_id is None:
            plant.location_id = None
        else:
            # Standort muss existieren und dem User gehören
            loc = Location.query.filter_by(id=location_id, user_id=user_id).first()
            if not loc:
                return jsonify({"error": "Standort ungültig"}), 400
            plant.location_id = location_id

    try:
        db.session.commit()
        return jsonify({"message": "Pflanze aktualisiert"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fehler beim Aktualisieren: {str(e)}"}), 400


# App starten
if __name__ == '__main__':
    app.run(debug=True)
