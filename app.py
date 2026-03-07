import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from models import db, User, Location, Plant, PlantCatalog

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

    # Beispiel-Pflanzen für den Pflanzenkatalog
    if PlantCatalog.query.count() == 0:
        try:
            example_plants = [
                PlantCatalog(
                    name="Monstera",
                    botanical_name="Monstera deliciosa",
                    light_requirement="halbschatten",
                    water_requirement="mittel",
                    temperature_requirement="normal",
                    humidity_requirement="normal",
                    soil_type="durchlaessig",
                    height_min=50,
                    height_max=200,
                    flower_color="weiß",
                    poisonous=True,
                    flowering_season_start=6,
                    flowering_season_end=8
                ),
                PlantCatalog(
                    name="Bogenhanf",
                    botanical_name="Sansevieria trifasciata",
                    light_requirement="schatten",
                    water_requirement="wenig",
                    temperature_requirement="normal",
                    humidity_requirement="trocken",
                    soil_type="kaktuserde",
                    height_min=30,
                    height_max=120,
                    flower_color="creme",
                    poisonous=True,
                    flowering_season_start=4,
                    flowering_season_end=6
                ),
                PlantCatalog(
                    name="Einblatt",
                    botanical_name="Spathiphyllum wallisii",
                    light_requirement="schatten",
                    water_requirement="mittel",
                    temperature_requirement="normal",
                    humidity_requirement="feucht",
                    soil_type="humos",
                    height_min=30,
                    height_max=80,
                    flower_color="weiß",
                    poisonous=True,
                    flowering_season_start=3,
                    flowering_season_end=9
                ),
                PlantCatalog(
                    name="Gummibaum",
                    botanical_name="Ficus elastica",
                    light_requirement="halbschatten",
                    water_requirement="mittel",
                    temperature_requirement="normal",
                    humidity_requirement="normal",
                    soil_type="durchlaessig",
                    height_min=60,
                    height_max=250,
                    flower_color="grün",
                    poisonous=True,
                    flowering_season_start=5,
                    flowering_season_end=7
                ),
                PlantCatalog(
                    name="Calathea",
                    botanical_name="Calathea orbifolia",
                    light_requirement="halbschatten",
                    water_requirement="mittel",
                    temperature_requirement="warm",
                    humidity_requirement="feucht",
                    soil_type="humos",
                    height_min=30,
                    height_max=90,
                    flower_color="violett",
                    poisonous=False,
                    flowering_season_start=6,
                    flowering_season_end=8
                ),
                PlantCatalog(
                    name="Aloe Vera",
                    botanical_name="Aloe barbadensis miller",
                    light_requirement="sonnig",
                    water_requirement="wenig",
                    temperature_requirement="warm",
                    humidity_requirement="trocken",
                    soil_type="kaktuserde",
                    height_min=20,
                    height_max=60,
                    flower_color="gelb",
                    poisonous=False,
                    flowering_season_start=5,
                    flowering_season_end=7
                ),
                PlantCatalog(
                    name="Zamioculcas",
                    botanical_name="Zamioculcas zamiifolia",
                    light_requirement="schatten",
                    water_requirement="wenig",
                    temperature_requirement="normal",
                    humidity_requirement="trocken",
                    soil_type="durchlaessig",
                    height_min=40,
                    height_max=100,
                    flower_color="grün",
                    poisonous=True,
                    flowering_season_start=4,
                    flowering_season_end=6
                ),
                PlantCatalog(
                    name="Orchidee",
                    botanical_name="Phalaenopsis",
                    light_requirement="halbschatten",
                    water_requirement="mittel",
                    temperature_requirement="warm",
                    humidity_requirement="feucht",
                    soil_type="orchideensubstrat",
                    height_min=20,
                    height_max=70,
                    flower_color="rosa",
                    poisonous=False,
                    flowering_season_start=1,
                    flowering_season_end=12
                )
            ]

            db.session.add_all(example_plants)
            db.session.commit()

            print("Beispiel-Pflanzen angelegt")

        except Exception as e:
            db.session.rollback()
            print(f"Fehler beim Anlegen der Beispiel-Pflanzen: {e}")

def require_login():
    '''
    Prüft, ob User eingeloggt
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

# 3-stufige Eignungsprüfung mit geeignet/bedingt geeignet/ungeeignet
def compare_enum_values(plant_value, location_value, ordered_values):
    '''
    Vergleicht Enum-Werte
    - "match" --> exakt passend
    - "close" --> nur eine Stufe Unterschied
    - "mismatch" --> mehr als eine Stufe Unterschied oder nicht vergleichbar
    '''
    if not plant_value or not location_value:
        return "unknown"

    if plant_value not in ordered_values or location_value not in ordered_values:
        return "unknown"

    plant_index = ordered_values.index(plant_value)
    location_index = ordered_values.index(location_value)

    difference = abs(plant_index - location_index)

    if difference == 0:
        return "match"
    elif difference == 1:
        return "close"
    else:
        return "mismatch"


def check_plant_location_suitability(plant, location):
    '''
    Prüft, ob eine Pflanze zu einem Standort passt
    Bewertung:
    - geeignet
    - bedingt geeignet
    - ungeeignet

    Grundlage:
    - Licht
    - Temperatur
    - Luftfeuchte
    '''
    checks = []

    # Reihenfolge der Enum-Werte
    light_scale = ["schatten", "halbschatten", "sonnig"]
    temp_scale = ["kalt", "normal", "warm"]
    humidity_scale = ["trocken", "normal", "feucht"]

    # Licht prüfen
    if plant.light_requirement:
        result = compare_enum_values(
            plant.light_requirement,
            location.lighting_condition,
            light_scale
        )
        checks.append({
            "criterion": "light",
            "plant_value": plant.light_requirement,
            "location_value": location.lighting_condition,
            "result": result
        })

    # Temperatur prüfen
    if plant.temperature_requirement:
        result = compare_enum_values(
            plant.temperature_requirement,
            location.temperature,
            temp_scale
        )
        checks.append({
            "criterion": "temperature",
            "plant_value": plant.temperature_requirement,
            "location_value": location.temperature,
            "result": result
        })

    # Luftfeuchte prüfen
    if plant.humidity_requirement:
        result = compare_enum_values(
            plant.humidity_requirement,
            location.humidity,
            humidity_scale
        )
        checks.append({
            "criterion": "humidity",
            "plant_value": plant.humidity_requirement,
            "location_value": location.humidity,
            "result": result
        })

    # Gesamtbewertung bestimmen
    match_count = sum(1 for check in checks if check["result"] == "match")
    close_count = sum(1 for check in checks if check["result"] == "close")
    mismatch_count = sum(1 for check in checks if check["result"] == "mismatch")

    if mismatch_count == 0 and close_count == 0:
        suitability = "geeignet"
    elif mismatch_count == 0 and close_count > 0:
        suitability = "bedingt geeignet"
    else:
        suitability = "ungeeignet"

    return {
        "plant_id": plant.id,
        "plant_name": plant.name,
        "location_id": location.id,
        "location_name": location.name,
        "suitability": suitability,
        "checks": checks
    }

# Pflanzenempfehlungen
def get_plant_identity(plant):
    '''
    Eindeutige Pflanzen-Identität zum Vergleich
    '''
    if getattr(plant, "botanical_name", None):
        return plant.botanical_name.strip().lower()
    return plant.name.strip().lower()


def get_height_mid(plant):
    '''
    Berechnet einen ungefähren Mittelwert der Pflanzenhöhe
    '''
    if plant.height_min is not None and plant.height_max is not None:
        return (plant.height_min + plant.height_max) / 2
    if plant.height_min is not None:
        return plant.height_min
    if plant.height_max is not None:
        return plant.height_max
    return None


def calculate_aesthetic_bonus(candidate, existing_plants_at_location):
    '''
    Vergibt kleine Bonuspunkte für ästhetische Vielfalt
    - andere Blütenfarbe als vorhandene Pflanzen = +1
    - deutlich andere Höhe als vorhandene Pflanzen = +1
    '''
    bonus = 0
    reasons = []

    # Blütenfarben der vorhandenen Pflanzen sammeln
    existing_colors = {
        p.flower_color.strip().lower()
        for p in existing_plants_at_location
        if p.flower_color
    }

    if candidate.flower_color:
        candidate_color = candidate.flower_color.strip().lower()
        if existing_colors and candidate_color not in existing_colors:
            bonus += 1
            reasons.append("abweichende_blütenfarbe")

    # Durchschnittliche Höhe der vorhandenen Pflanzen vergleichen
    existing_heights = [
        get_height_mid(p)
        for p in existing_plants_at_location
        if get_height_mid(p) is not None
    ]
    candidate_height = get_height_mid(candidate)

    if existing_heights and candidate_height is not None:
        avg_existing_height = sum(existing_heights) / len(existing_heights)

        # Regel: ab 30 cm Unterschied gilt als variabel
        if abs(candidate_height - avg_existing_height) >= 30:
            bonus += 1
            reasons.append("abweichende_pflanzenhöhe")

    return bonus, reasons

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
        return redirect(url_for('auth'))
    
    # User ist eingeloggt -> index.html anzeigen
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
def wishlist_page():
    '''
    HTML-Seite für die Wunschliste anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template('wunschliste.html', username=session['username'])


@app.route('/inventory', methods=['GET'])
def inventory_page():
    '''
    HTML-Seite für den Bestand anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template('bestand.html', username=session['username'])


@app.route('/locations', methods=['GET'])
def locations_page():
    '''
    HTML-Seite für die Standorte anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template('standorte.html', username=session['username'])


@app.route('/plants', methods=['GET'])
def plants_page():
    '''
    HTML-Seite für die Gesamtübersicht aller Pflanzen anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template(
        'liste_von_pflanzen.html',
        username=session['username']
    )

@app.route('/locations/<int:location_id>/plants', methods=['GET'])
def location_plants_page(location_id):
    '''
    HTML-Seite für Pflanzen eines Standorts anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template(
        'liste_von_pflanzen.html',
        username=session['username'],
        location_id=location_id
    )


@app.route('/new_plant', methods=['GET'])
def new_plant_page():
    '''
    HTML-Seite zum Anlegen einer neuen Pflanze anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template('neue_pflanze.html', username=session['username'])


@app.route('/plants/<int:plant_id>/edit', methods=['GET'])
def edit_plant_page(plant_id):
    '''
    HTML-Seite zum Ändern einer Pflanze anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template(
        'aenderung.html',
        username=session['username'],
        plant_id=plant_id
    )


@app.route('/locations/<int:location_id>/edit', methods=['GET'])
def edit_location_page(location_id):
    '''
    HTML-Seite zum Ändern eines Standorts anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    return render_template(
        'aendern_standort.html',
        username=session['username'],
        location_id=location_id
    )

@app.route('/api/wishlist', methods=['GET'])
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
            "temperature_requirement": p.temperature_requirement,
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

    ok, err = validate_enum("light_requirement", data.get("light_requirement"), ALLOWED_LIGHT)
    if not ok:
        return err

    ok, err = validate_enum("water_requirement", data.get("water_requirement"), ALLOWED_WATER)
    if not ok:
        return err

    ok, err = validate_enum("humidity_requirement", data.get("humidity_requirement"), ALLOWED_HUMIDITY)
    if not ok:
        return err

    ok, err = validate_enum("temperature_requirement", data.get("temperature_requirement"), ALLOWED_TEMP)
    if not ok:
        return err

    try:
        plant = Plant(
            user_id=user_id,
            name=name,
            botanical_name=data.get("botanical_name"),

            light_requirement=data.get("light_requirement"),
            water_requirement=data.get("water_requirement"),
            temperature_requirement=data.get("temperature_requirement"),
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


@app.route('/api/locations', methods=['GET'])
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


@app.route('/api/locations', methods=['POST'])
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


@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
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


@app.route('/api/locations/<int:location_id>/plants', methods=['GET'])
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

@app.route('/api/plants/<int:plant_id>/check-location/<int:location_id>', methods=['GET'])
def check_plant_for_location(plant_id, location_id):
    '''
    Prüft ob Pflanze zu Standort passt
    '''
    user_id, err = require_login()
    if err:
        return err

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id).first()
    if not plant:
        return jsonify({"error": "Pflanze nicht gefunden"}), 404

    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Standort nicht gefunden"}), 404

    result = check_plant_location_suitability(plant, location)
    return jsonify(result), 200

# Geeignete Standorte für eine Wunschlisten-Pflanze vorschlagen
@app.route('/api/plants/<int:plant_id>/suggest-locations', methods=['GET'])
def suggest_locations_for_plant(plant_id):
    '''
    Schlägt für eine Pflanze aus der Wunschliste geeignete Standorte vor.
    '''
    user_id, err = require_login()
    if err:
        return err

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id, is_purchased=False).first()
    if not plant:
        return jsonify({"error": "Pflanze aus Wunschliste nicht gefunden"}), 404

    locations = Location.query.filter_by(user_id=user_id).order_by(Location.created_at.desc()).all()

    results = []
    for location in locations:
        result = check_plant_location_suitability(plant, location)
        results.append(result)

    # Nur geeignete oder bedingt geeignete Standorte zurückgeben
    filtered_results = [
        r for r in results
        if r["suitability"] in ["geeignet", "bedingt geeignet"]
    ]

    # Geeignet vor bedingt geeignet sortieren
    order = {"geeignet": 0, "bedingt geeignet": 1}
    filtered_results.sort(key=lambda r: order.get(r["suitability"], 99))

    return jsonify(filtered_results), 200

@app.route('/api/inventory', methods=['GET'])
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

@app.route('/api/plants', methods=['GET'])
def list_all_plants():
    '''
    Gibt eine Gesamtliste aller Pflanzen des eingeloggten Users zurück
    Enthält Wunschliste und Bestand
    '''
    user_id, err = require_login()
    if err:
        return err

    plants = Plant.query.filter_by(user_id=user_id).order_by(Plant.created_at.desc()).all()

    result = []
    for p in plants:
        location_name = None

        if p.location_id is not None:
            location = Location.query.filter_by(id=p.location_id, user_id=user_id).first()
            if location:
                location_name = location.name

        result.append({
            "id": p.id,
            "name": p.name,
            "botanical_name": p.botanical_name,
            "is_purchased": bool(p.is_purchased),
            "location_id": p.location_id,
            "location_name": location_name,
            "light_requirement": p.light_requirement,
            "water_requirement": p.water_requirement,
            "temperature_requirement": p.temperature_requirement,
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
        })

    return jsonify(result), 200

@app.route('/api/inventory', methods=['POST'])
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


@app.route('/api/plants/<int:plant_id>', methods=['PATCH'])
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

    if "temperature_requirement" in data:
        ok, err = validate_enum("temperature_requirement",
                                data.get("temperature_requirement"),
                                ALLOWED_TEMP)
        if not ok:
            return err

        plant.temperature_requirement = data.get("temperature_requirement")

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
