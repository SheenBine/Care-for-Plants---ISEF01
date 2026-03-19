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

    if Location.query.count() == 0:

        user = User.query.filter_by(username="testuser").first()

        wohnzimmer = Location(
            user_id=user.id,
            name="Wohnzimmer",
            lighting_condition="halbschatten",
            temperature="normal",
            humidity="normal"
        )

        schlafzimmer = Location(
            user_id=user.id,
            name="Schlafzimmer",
            lighting_condition="schatten",
            temperature="normal",
            humidity="trocken"
        )

        db.session.add_all([wohnzimmer, schlafzimmer])
        db.session.commit()

    if Plant.query.count() == 0:

        user = User.query.filter_by(username="testuser").first()
        wohnzimmer = Location.query.filter_by(name="Wohnzimmer").first()

        monstera = Plant(
            user_id=user.id,
            name="Monstera",
            botanical_name="Monstera deliciosa",
            light_requirement="halbschatten",
            water_requirement="mittel",
            temperature_requirement="normal",
            humidity_requirement="normal",
            is_purchased=True,
            location_id=wohnzimmer.id
        )

        ficus = Plant(
            user_id=user.id,
            name="Gummibaum",
            botanical_name="Ficus elastica",
            light_requirement="halbschatten",
            water_requirement="mittel",
            temperature_requirement="normal",
            humidity_requirement="normal",
            is_purchased=False
        )

        db.session.add_all([monstera, ficus])
        db.session.commit()

def require_login():
    '''
    Prüft, ob User eingeloggt
    '''
    user_id = session.get('user_id')
    if not user_id:
        return None, (jsonify({"error": "Nicht eingeloggt"}), 401)
    return user_id, None

def get_logged_in_user_id():
    '''
    Liefert die user_id aus der Session für HTML-Seiten
    Gibt None zurück, wenn niemand eingeloggt ist
    '''
    return session.get('user_id')


def get_user_locations(user_id):
    '''
    Lädt alle Standorte des Users, absteigend nach Erstellzeit
    '''
    return Location.query.filter_by(user_id=user_id).order_by(Location.name.asc()).all()


def get_selected_location(user_id):
    '''
    Liest location_id aus der URL (?location_id=...)
    und liefert das passende Location-Objekt oder None
    '''
    location_id = request.args.get('location_id', type=int)

    if location_id is None:
        return None

    return Location.query.filter_by(id=location_id, user_id=user_id).first()


def get_location_name_map(user_id):
    '''
    Baut ein Dictionary:
    {location_id: location_name}
    '''
    locations = get_user_locations(user_id)
    return {loc.id: loc.name for loc in locations}


def add_location_name_to_plants(plants, user_id):
    '''
    Wandelt Pflanzenobjekte in Dictionaries um
    und ergänzt location_name
    '''
    location_map = get_location_name_map(user_id)

    result = []
    for p in plants:
        result.append({
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
            "is_purchased": bool(p.is_purchased),
            "location_id": p.location_id,
            "location_name": location_map.get(p.location_id),
            "created_at": str(p.created_at)
        })

    return result

def build_plant_data(plant, user_id):
    '''
    Baut ein Dictionary für genau eine Pflanze
    '''
    location_name = None
    if plant.location_id is not None:
        location = Location.query.filter_by(id=plant.location_id, user_id=user_id).first()
        if location:
            location_name = location.name

    return {
        "id": plant.id,
        "name": plant.name,
        "botanical_name": plant.botanical_name,
        "light_requirement": plant.light_requirement,
        "water_requirement": plant.water_requirement,
        "temperature_requirement": plant.temperature_requirement,
        "humidity_requirement": plant.humidity_requirement,
        "soil_type": plant.soil_type,
        "height_min": plant.height_min,
        "height_max": plant.height_max,
        "poisonous": bool(plant.poisonous),
        "flowering_season_start": plant.flowering_season_start,
        "flowering_season_end": plant.flowering_season_end,
        "flower_color": plant.flower_color,
        "notes": plant.notes,
        "is_purchased": bool(plant.is_purchased),
        "location_id": plant.location_id,
        "location_name": location_name
    }

def parse_location_id_from_form(user_id):
    '''
    Liest location_id aus request.form
    Leerer Wert bedeutet: kein Standort
    '''
    raw_location_id = request.form.get('location_id')

    if raw_location_id is None or raw_location_id == "":
        return None, None

    try:
        location_id = int(raw_location_id)
    except ValueError:
        return None, "Ungültige Standort-ID"

    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return None, "Standort ungültig"

    return location_id, None

# Validierung der Enum-Felder

ALLOWED_LIGHT = {"schatten", "halbschatten", "sonnig"}
ALLOWED_TEMP = {"kalt", "normal", "warm"}
ALLOWED_HUMIDITY = {"trocken", "normal", "feucht"}
ALLOWED_WATER = {"wenig", "mittel", "viel"}

def validate_enum(field_name, value, allowed_values):
    '''
    Prüft, ob ein Wert in einer erlaubten Menge liegt.
    - None oder "" wird als "nicht gesetzt" akzeptiert
    '''
    if value is None:
        return True, None

    if isinstance(value, str) and value.strip() == "":
        return True, None

    if value not in allowed_values:
        allowed_text = ", ".join(sorted(allowed_values))
        return False, f"Ungültiger Wert für {field_name}: '{value}'. Erlaubt sind: {allowed_text}"

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
    Login und Registrierung auf einer Seite
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
                return render_template('login.html', error="Benutzer existiert bereits!")
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
                return render_template('login.html', error=f"Fehler bei der Registrierung: {str(e)}")

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
                return render_template('login.html', error="Login fehlgeschlagen!")

    # Standardmäßig GET, um Login/Registrierung zu zeigen
    return render_template('login.html', error=None)


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
    Optional nach Standort filterbar über ?location_id=
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = get_logged_in_user_id()
    locations = get_user_locations(user_id)
    selected_location = get_selected_location(user_id)

    query = Plant.query.filter_by(user_id=user_id, is_purchased=False)

    if selected_location is not None:
        query = query.filter_by(location_id=selected_location.id)

    plants = query.order_by(Plant.created_at.desc()).all()
    plants_data = add_location_name_to_plants(plants, user_id)

    return render_template(
        'wunschliste.html',
        username=session['username'],
        locations=locations,
        plants=plants_data,
        selected_location_id=selected_location.id if selected_location else None,
        error=None
    )


@app.route('/inventory', methods=['GET'])
def inventory_page():
    '''
    HTML-Seite für den Bestand anzeigen
    Optional nach Standort filterbar über ?location_id=
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = get_logged_in_user_id()
    locations = get_user_locations(user_id)
    selected_location = get_selected_location(user_id)

    query = Plant.query.filter_by(user_id=user_id, is_purchased=True)

    if selected_location is not None:
        query = query.filter_by(location_id=selected_location.id)

    plants = query.order_by(Plant.created_at.desc()).all()
    plants_data = add_location_name_to_plants(plants, user_id)

    return render_template(
        'bestand.html',
        username=session['username'],
        locations=locations,
        plants=plants_data,
        selected_location_id=selected_location.id if selected_location else None,
        error=None
    )


@app.route('/locations', methods=['GET'])
def locations_page():
    '''
    HTML-Seite für die Standorte anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']
    locations = get_user_locations(user_id)

    return render_template(
        'standorte.html',
        username=session['username'],
        locations=locations,
        error=None
    )


@app.route('/plants', methods=['GET'])
def plants_page():
    '''
    HTML-Seite für Pflanzenempfehlungen anzeigen
    Optional nach Standort filterbar über ?location_id=
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = get_logged_in_user_id()
    locations = get_user_locations(user_id)
    selected_location = get_selected_location(user_id)

    all_user_plants = Plant.query.filter_by(user_id=user_id).all()
    owned_plant_keys = {get_plant_identity(p) for p in all_user_plants}

    inventory_plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).all()

    if selected_location is not None:
        inventory_plants_for_bonus = Plant.query.filter_by(
            user_id=user_id,
            is_purchased=True,
            location_id=selected_location.id
        ).all()
    else:
        inventory_plants_for_bonus = inventory_plants

    catalog_plants = PlantCatalog.query.order_by(PlantCatalog.name.asc()).all()

    recommendations = []

    for catalog_plant in catalog_plants:
        if get_plant_identity(catalog_plant) in owned_plant_keys:
            continue

        suitability = None
        checks = []

        if selected_location is not None:
            suitability_result = check_plant_location_suitability(catalog_plant, selected_location)

            if suitability_result["suitability"] not in ["geeignet", "bedingt geeignet"]:
                continue

            suitability = suitability_result["suitability"]
            checks = suitability_result["checks"]

        aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(
            catalog_plant,
            inventory_plants_for_bonus
        )

        recommendations.append({
            "id": catalog_plant.id,
            "name": catalog_plant.name,
            "botanical_name": catalog_plant.botanical_name,
            "light_requirement": catalog_plant.light_requirement,
            "water_requirement": catalog_plant.water_requirement,
            "temperature_requirement": catalog_plant.temperature_requirement,
            "humidity_requirement": catalog_plant.humidity_requirement,
            "soil_type": catalog_plant.soil_type,
            "height_min": catalog_plant.height_min,
            "height_max": catalog_plant.height_max,
            "poisonous": bool(catalog_plant.poisonous),
            "flowering_season_start": catalog_plant.flowering_season_start,
            "flowering_season_end": catalog_plant.flowering_season_end,
            "flower_color": catalog_plant.flower_color,
            "notes": None,
            "location_id": selected_location.id if selected_location else None,
            "location_name": selected_location.name if selected_location else None,
            "suitability": suitability,
            "checks": checks,
            "aesthetic_bonus": aesthetic_bonus,
            "aesthetic_reasons": aesthetic_reasons,
            "created_at": str(catalog_plant.created_at)
        })

    suitability_order = {
        "geeignet": 0,
        "bedingt geeignet": 1,
        None: 2
    }

    recommendations.sort(
        key=lambda r: (
            suitability_order.get(r["suitability"], 99),
            -r["aesthetic_bonus"],
            r["name"].lower()
        )
    )

    return render_template(
        'liste_von_pflanzen.html',
        username=session['username'],
        locations=locations,
        plants=recommendations,
        selected_location_id=selected_location.id if selected_location else None,
        error=None
    )


@app.route('/new_plant', methods=['GET'])
def new_plant_page():
    '''
    HTML-Seite zum Anlegen einer neuen Pflanze anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))
    
    locations = get_user_locations(session['user_id'])

    return render_template(
    'neue_pflanze.html',
    username=session['username'],
    locations=locations,
    error=None
)

@app.route('/plants/create', methods=['POST'])
def create_plant():
    '''
    Neue Pflanze anlegen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']
    locations = get_user_locations(user_id)

    name = (request.form.get('name') or "").strip()
    botanical_name = request.form.get('botanical_name')
    light_requirement = request.form.get('light_requirement')
    water_requirement = request.form.get('water_requirement')
    temperature_requirement = request.form.get('temperature_requirement')
    humidity_requirement = request.form.get('humidity_requirement')
    soil_type = request.form.get('soil_type')
    height_min = request.form.get('height_min') or None
    height_max = request.form.get('height_max') or None
    flower_color = request.form.get('flower_color')
    flowering_season_start = request.form.get('flowering_season_start') or None
    flowering_season_end = request.form.get('flowering_season_end') or None
    notes = request.form.get('notes')
    poisonous = request.form.get('poisonous') == 'on'
    is_purchased = request.form.get('is_purchased') == 'on'

    if not name:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error="Bitte einen Namen eingeben."
        )

    ok, err = validate_enum("light_requirement", light_requirement, ALLOWED_LIGHT)
    if not ok:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=err
        )

    ok, err = validate_enum("water_requirement", water_requirement, ALLOWED_WATER)
    if not ok:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=err
        )

    ok, err = validate_enum("temperature_requirement", temperature_requirement, ALLOWED_TEMP)
    if not ok:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=err
        )

    ok, err = validate_enum("humidity_requirement", humidity_requirement, ALLOWED_HUMIDITY)
    if not ok:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=err
        )

    location_id, location_error = parse_location_id_from_form(user_id)
    if location_error:
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=location_error
        )

    try:
        plant = Plant(
            user_id=user_id,
            name=name,
            botanical_name=botanical_name,
            light_requirement=light_requirement or None,
            water_requirement=water_requirement or None,
            temperature_requirement=temperature_requirement or None,
            humidity_requirement=humidity_requirement or None,
            soil_type=soil_type,
            height_min=int(height_min) if height_min else None,
            height_max=int(height_max) if height_max else None,
            poisonous=poisonous,
            flowering_season_start=int(flowering_season_start) if flowering_season_start else None,
            flowering_season_end=int(flowering_season_end) if flowering_season_end else None,
            flower_color=flower_color,
            notes=notes,
            is_purchased=is_purchased,
            location_id=location_id
        )

        db.session.add(plant)
        db.session.commit()

        if is_purchased:
            return redirect(url_for('inventory_page'))
        return redirect(url_for('wishlist_page'))

    except Exception as e:
        db.session.rollback()
        return render_template(
            'neue_pflanze.html',
            username=session['username'],
            locations=locations,
            error=f"Fehler beim Speichern: {str(e)}"
        )

@app.route('/plants/<int:plant_id>/edit', methods=['GET'])
def edit_plant_page(plant_id):
    '''
    HTML-Seite zum Ändern einer Pflanze anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id).first()
    if not plant:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=None,
            locations=[],
            error="Pflanze nicht gefunden"
        )

    locations = get_user_locations(user_id)

    plant_data = build_plant_data(plant, user_id)

    return render_template(
        'aenderung.html',
        username=session['username'],
        plant=plant_data,
        locations=locations,
        error=None
    )

@app.route('/plants/<int:plant_id>/update', methods=['POST'])
def update_plant_form(plant_id):
    '''
    Pflanze über HTML-Formular bearbeiten und speichern
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']
    locations = get_user_locations(user_id)

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id).first()
    if not plant:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=None,
            locations=locations,
            error="Pflanze nicht gefunden"
        )

    name = (request.form.get('name') or "").strip()
    botanical_name = request.form.get('botanical_name')
    light_requirement = request.form.get('light_requirement')
    water_requirement = request.form.get('water_requirement')
    temperature_requirement = request.form.get('temperature_requirement')
    humidity_requirement = request.form.get('humidity_requirement')
    soil_type = request.form.get('soil_type')
    height_min = request.form.get('height_min') or None
    height_max = request.form.get('height_max') or None
    flower_color = request.form.get('flower_color')
    flowering_season_start = request.form.get('flowering_season_start') or None
    flowering_season_end = request.form.get('flowering_season_end') or None
    notes = request.form.get('notes')
    poisonous = request.form.get('poisonous') == 'on'
    is_purchased = request.form.get('is_purchased') == 'on'

    if not name:
        plant_data = build_plant_data(plant, user_id)

        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=plant_data,
            locations=locations,
            error="Bitte einen Namen eingeben."
        )

    ok, err = validate_enum("light_requirement", light_requirement, ALLOWED_LIGHT)
    if not ok:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=err
        )

    ok, err = validate_enum("water_requirement", water_requirement, ALLOWED_WATER)
    if not ok:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=err
        )

    ok, err = validate_enum("temperature_requirement", temperature_requirement, ALLOWED_TEMP)
    if not ok:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=err
        )

    ok, err = validate_enum("humidity_requirement", humidity_requirement, ALLOWED_HUMIDITY)
    if not ok:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=err
        )

    location_id, location_error = parse_location_id_from_form(user_id)
    if location_error:
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=location_error
        )

    try:
        plant.name = name
        plant.botanical_name = botanical_name
        plant.light_requirement = light_requirement or None
        plant.water_requirement = water_requirement or None
        plant.temperature_requirement = temperature_requirement or None
        plant.humidity_requirement = humidity_requirement or None
        plant.soil_type = soil_type
        plant.height_min = int(height_min) if height_min else None
        plant.height_max = int(height_max) if height_max else None
        plant.poisonous = poisonous
        plant.flowering_season_start = int(flowering_season_start) if flowering_season_start else None
        plant.flowering_season_end = int(flowering_season_end) if flowering_season_end else None
        plant.flower_color = flower_color
        plant.notes = notes
        plant.is_purchased = is_purchased
        plant.location_id = location_id

        db.session.commit()

        if is_purchased:
            return redirect(url_for('inventory_page'))
        return redirect(url_for('wishlist_page'))

    except Exception as e:
        db.session.rollback()
        return render_template(
            'aenderung.html',
            username=session['username'],
            plant=build_plant_data(plant, user_id),
            locations=locations,
            error=f"Fehler beim Speichern: {str(e)}"
        )

@app.route('/plants/<int:plant_id>/delete', methods=['POST'])
def delete_plant(plant_id):
    '''
    Pflanze aus Wunschliste oder Bestand löschen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id).first()
    if not plant:
        return redirect(url_for('wishlist_page'))

    was_purchased = bool(plant.is_purchased)

    try:
        db.session.delete(plant)
        db.session.commit()

        if was_purchased:
            return redirect(url_for('inventory_page'))
        return redirect(url_for('wishlist_page'))

    except Exception:
        db.session.rollback()

        if was_purchased:
            locations = get_user_locations(user_id)
            query = Plant.query.filter_by(user_id=user_id, is_purchased=True)
            plants = query.order_by(Plant.created_at.desc()).all()
            plants_data = add_location_name_to_plants(plants, user_id)

            return render_template(
                'bestand.html',
                username=session['username'],
                locations=locations,
                plants=plants_data,
                selected_location_id=None,
                error="Fehler beim Löschen der Pflanze."
            )

        locations = get_user_locations(user_id)
        query = Plant.query.filter_by(user_id=user_id, is_purchased=False)
        plants = query.order_by(Plant.created_at.desc()).all()
        plants_data = add_location_name_to_plants(plants, user_id)

        return render_template(
            'wunschliste.html',
            username=session['username'],
            locations=locations,
            plants=plants_data,
            selected_location_id=None,
            error="Fehler beim Löschen der Pflanze."
        )

@app.route('/locations/<int:location_id>/edit', methods=['GET'])
def edit_location_page(location_id):
    '''
    HTML-Seite zum Ändern eines Standorts anzeigen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=None,
            error="Standort nicht gefunden"
        )

    location_data = {
        "id": location.id,
        "name": location.name,
        "lighting_condition": location.lighting_condition,
        "temperature": location.temperature,
        "humidity": location.humidity,
        "description": location.description
    }

    return render_template(
        'aendern_standort.html',
        username=session['username'],
        location=location_data,
        error=None
    )

@app.route('/api/wishlist', methods=['GET'])
def list_wishlist():
    '''
    Wunschliste anzeigen. Also Plants mit is_purchased = False
    '''
    user_id, err = require_login()
    if err:
        return err
    
    location_id = request.args.get("location_id", type=int)

    query = Plant.query.filter_by(user_id=user_id, is_purchased=False)  

    if location_id is not None:
        query = query.filter_by(location_id=location_id)  

    plants = query.order_by(Plant.created_at.desc()).all()  

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
            "location_id": p.location_id,
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
        return jsonify({"error": err}), 400

    ok, err = validate_enum("water_requirement", data.get("water_requirement"), ALLOWED_WATER)
    if not ok:
        return err

    ok, err = validate_enum("humidity_requirement", data.get("humidity_requirement"), ALLOWED_HUMIDITY)
    if not ok:
        return jsonify({"error": err}), 400

    ok, err = validate_enum("temperature_requirement", data.get("temperature_requirement"), ALLOWED_TEMP)
    if not ok:
        return jsonify({"error": err}), 400

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

            is_purchased=False,
            location_id=location_id
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

@app.route('/plants/<int:plant_id>/move-to-inventory', methods=['POST'])
def move_plant_to_inventory(plant_id):
    '''
    Pflanze von Wunschliste in Bestand verschieben
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    plant = Plant.query.filter_by(id=plant_id, user_id=user_id, is_purchased=False).first()
    if not plant:
        return redirect(url_for('wishlist_page'))

    try:
        plant.is_purchased = True
        db.session.commit()
        return redirect(url_for('inventory_page'))

    except Exception:
        db.session.rollback()

        locations = get_user_locations(user_id)
        query = Plant.query.filter_by(user_id=user_id, is_purchased=False)
        plants = query.order_by(Plant.created_at.desc()).all()
        plants_data = add_location_name_to_plants(plants, user_id)

        return render_template(
            'wunschliste.html',
            username=session['username'],
            locations=locations,
            plants=plants_data,
            selected_location_id=None,
            error="Fehler beim Verschieben in den Bestand."
        )

@app.route('/catalog/<int:catalog_plant_id>/add-to-wishlist', methods=['POST'])
def add_catalog_plant_to_wishlist(catalog_plant_id):
    '''
    Pflanze aus dem Katalog zur Wunschliste hinzufügen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    catalog_plant = PlantCatalog.query.filter_by(id=catalog_plant_id).first()
    if not catalog_plant:
        return redirect(url_for('plants_page'))

    existing_plants = Plant.query.filter_by(user_id=user_id).all()
    existing_keys = {get_plant_identity(p) for p in existing_plants}

    if get_plant_identity(catalog_plant) in existing_keys:
        locations = get_user_locations(user_id)
        selected_location = get_selected_location(user_id)

        all_user_plants = Plant.query.filter_by(user_id=user_id).all()
        owned_plant_keys = {get_plant_identity(p) for p in all_user_plants}
        inventory_plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).all()

        if selected_location is not None:
            inventory_plants_for_bonus = Plant.query.filter_by(
                user_id=user_id,
                is_purchased=True,
                location_id=selected_location.id
            ).all()
        else:
            inventory_plants_for_bonus = inventory_plants

        catalog_plants = PlantCatalog.query.order_by(PlantCatalog.name.asc()).all()
        recommendations = []

        for cp in catalog_plants:
            if get_plant_identity(cp) in owned_plant_keys:
                continue

            suitability = None
            checks = []

            if selected_location is not None:
                suitability_result = check_plant_location_suitability(cp, selected_location)
                if suitability_result["suitability"] not in ["geeignet", "bedingt geeignet"]:
                    continue
                suitability = suitability_result["suitability"]
                checks = suitability_result["checks"]

            aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(
                cp,
                inventory_plants_for_bonus
            )

            recommendations.append({
                "id": cp.id,
                "name": cp.name,
                "botanical_name": cp.botanical_name,
                "light_requirement": cp.light_requirement,
                "water_requirement": cp.water_requirement,
                "temperature_requirement": cp.temperature_requirement,
                "humidity_requirement": cp.humidity_requirement,
                "soil_type": cp.soil_type,
                "height_min": cp.height_min,
                "height_max": cp.height_max,
                "poisonous": bool(cp.poisonous),
                "flowering_season_start": cp.flowering_season_start,
                "flowering_season_end": cp.flowering_season_end,
                "flower_color": cp.flower_color,
                "notes": None,
                "location_id": selected_location.id if selected_location else None,
                "location_name": selected_location.name if selected_location else None,
                "suitability": suitability,
                "checks": checks,
                "aesthetic_bonus": aesthetic_bonus,
                "aesthetic_reasons": aesthetic_reasons,
                "created_at": str(cp.created_at)
            })

        suitability_order = {
            "geeignet": 0,
            "bedingt geeignet": 1,
            None: 2
        }

        recommendations.sort(
            key=lambda r: (
                suitability_order.get(r["suitability"], 99),
                -r["aesthetic_bonus"],
                r["name"].lower()
            )
        )

        return render_template(
            'liste_von_pflanzen.html',
            username=session['username'],
            locations=locations,
            plants=recommendations,
            selected_location_id=selected_location.id if selected_location else None,
            error="Diese Pflanze ist bereits in Wunschliste oder Bestand vorhanden."
        )

    try:
        plant = Plant(
            user_id=user_id,
            name=catalog_plant.name,
            botanical_name=catalog_plant.botanical_name,
            light_requirement=catalog_plant.light_requirement,
            water_requirement=catalog_plant.water_requirement,
            temperature_requirement=catalog_plant.temperature_requirement,
            humidity_requirement=catalog_plant.humidity_requirement,
            soil_type=catalog_plant.soil_type,
            height_min=catalog_plant.height_min,
            height_max=catalog_plant.height_max,
            poisonous=bool(catalog_plant.poisonous),
            flowering_season_start=catalog_plant.flowering_season_start,
            flowering_season_end=catalog_plant.flowering_season_end,
            flower_color=catalog_plant.flower_color,
            notes=None,
            is_purchased=False,
            location_id=None
        )

        db.session.add(plant)
        db.session.commit()
        return redirect(url_for('wishlist_page'))

    except Exception:
        db.session.rollback()
        return redirect(url_for('plants_page'))

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
        return jsonify({"error": err}), 400

    ok, err = validate_enum("temperature", data.get("temperature"), ALLOWED_TEMP)
    if not ok:
        return jsonify({"error": err}), 400

    ok, err = validate_enum("humidity", data.get("humidity"), ALLOWED_HUMIDITY)
    if not ok:
        return jsonify({"error": err}), 400

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

# Pflanzenempfehlungen für einen Standort

@app.route('/api/locations/<int:location_id>/recommend-plants', methods=['GET'])
def recommend_plants_for_location(location_id):
    '''
    Empfiehlt Pflanzen aus dem PlantCatalog für einen Standort
    Kriterien:
    - Standortanforderungen müssen passen
    - bereits vorhandene Pflanzen des Users nicht doppelt vorschlagen
    - ästhetische Vielfalt leicht bevorzugen
    '''
    user_id, err = require_login()
    if err:
        return err

    # Standort prüfen
    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Standort nicht gefunden"}), 404

    # Bereits vorhandene Bestands-Pflanzen des Users holen
    inventory_plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).all()

    # Bereits vorhandene Pflanzen an genau diesem Standort holen
    inventory_plants_at_location = Plant.query.filter_by(
        user_id=user_id,
        is_purchased=True,
        location_id=location_id
    ).all()

    # Vorhandene Pflanzen-Identitäten zum Ausschließen sammeln
    owned_plant_keys = {get_plant_identity(p) for p in inventory_plants}

    # Alle Pflanzen aus dem Katalog holen
    catalog_plants = PlantCatalog.query.order_by(PlantCatalog.name.asc()).all()

    recommendations = []

    for catalog_plant in catalog_plants:
        # Keine Pflanzen empfehlen, die der User schon im Bestand hat
        if get_plant_identity(catalog_plant) in owned_plant_keys:
            continue

        # Standortprüfung mit vorhandener Logik
        suitability_result = check_plant_location_suitability(catalog_plant, location)

        # Nur geeignete oder bedingt geeignete Pflanzen vorschlagen
        if suitability_result["suitability"] not in ["geeignet", "bedingt geeignet"]:
            continue

        # Kleine ästhetische Bonuslogik
        aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(
            catalog_plant,
            inventory_plants_at_location
        )

        recommendations.append({
            "id": catalog_plant.id,
            "name": catalog_plant.name,
            "botanical_name": catalog_plant.botanical_name,
            "suitability": suitability_result["suitability"],
            "checks": suitability_result["checks"],
            "flower_color": catalog_plant.flower_color,
            "height_min": catalog_plant.height_min,
            "height_max": catalog_plant.height_max,
            "aesthetic_bonus": aesthetic_bonus,
            "aesthetic_reasons": aesthetic_reasons
        })

    # Sortierung:
    # geeignet vor bedingt geeignet
    # höherer ästhetischer Bonus zuerst
    # alphabetisch
    suitability_order = {
        "geeignet": 0,
        "bedingt geeignet": 1
    }

    recommendations.sort(
        key=lambda r: (
            suitability_order.get(r["suitability"], 99),
            -r["aesthetic_bonus"],
            r["name"].lower()
        )
    )

    return jsonify({
        "location_id": location.id,
        "location_name": location.name,
        "recommendations": recommendations
    }), 200

@app.route('/api/recommendations', methods=['GET'])  
def list_recommendations():  
    '''  
    Gibt Pflanzen aus dem PlantCatalog zurück,  
    die noch nicht in Wunschliste oder Bestand des Users vorhanden sind
    '''  
    user_id, err = require_login()  
    if err:  
        return err  

    location_id = request.args.get("location_id", type=int)  

    selected_location = None  
    if location_id is not None:  
        selected_location = Location.query.filter_by(id=location_id, user_id=user_id).first()  
        if not selected_location:  
            return jsonify({"error": "Standort nicht gefunden"}), 404  

    all_user_plants = Plant.query.filter_by(user_id=user_id).all()  
    owned_plant_keys = {get_plant_identity(p) for p in all_user_plants}  

    inventory_plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).all()  

    if selected_location is not None:  
        inventory_plants_for_bonus = Plant.query.filter_by(  
            user_id=user_id,  
            is_purchased=True,  
            location_id=location_id  
        ).all()  
    else:  
        inventory_plants_for_bonus = inventory_plants  

    catalog_plants = PlantCatalog.query.order_by(PlantCatalog.name.asc()).all()  

    recommendations = []  

    for catalog_plant in catalog_plants:  
        if get_plant_identity(catalog_plant) in owned_plant_keys:  
            continue  

        suitability = None  
        checks = []  

        if selected_location is not None:  
            suitability_result = check_plant_location_suitability(catalog_plant, selected_location)  

            if suitability_result["suitability"] not in ["geeignet", "bedingt geeignet"]:  
                continue  

            suitability = suitability_result["suitability"]  
            checks = suitability_result["checks"]  

        aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(  
            catalog_plant,  
            inventory_plants_for_bonus  
        )  

        recommendations.append({  
            "id": catalog_plant.id,  
            "name": catalog_plant.name,  
            "botanical_name": catalog_plant.botanical_name,  
            "light_requirement": catalog_plant.light_requirement,  
            "water_requirement": catalog_plant.water_requirement,  
            "temperature_requirement": catalog_plant.temperature_requirement,  
            "humidity_requirement": catalog_plant.humidity_requirement,  
            "soil_type": catalog_plant.soil_type,  
            "height_min": catalog_plant.height_min,  
            "height_max": catalog_plant.height_max,  
            "poisonous": bool(catalog_plant.poisonous),  
            "flowering_season_start": catalog_plant.flowering_season_start,  
            "flowering_season_end": catalog_plant.flowering_season_end,  
            "flower_color": catalog_plant.flower_color,  
            "notes": None,  
            "location_id": location_id if selected_location is not None else None,  
            "suitability": suitability,  
            "checks": checks,  
            "aesthetic_bonus": aesthetic_bonus,  
            "aesthetic_reasons": aesthetic_reasons,  
            "created_at": str(catalog_plant.created_at)  
        })  

    suitability_order = {  
        "geeignet": 0,  
        "bedingt geeignet": 1,  
        None: 2  
    }  

    recommendations.sort(  
        key=lambda r: (  
            suitability_order.get(r["suitability"], 99),  
            -r["aesthetic_bonus"],  
            r["name"].lower()  
        )  
    )  

    return jsonify(recommendations), 200  

@app.route('/api/inventory', methods=['GET'])
def list_inventory():
    '''
    Bestand anzeigen
    Das sind Plants mit is_purchased = True
    '''
    user_id, err = require_login()
    if err:
        return err

    location_id = request.args.get("location_id", type=int)

    query = Plant.query.filter_by(user_id=user_id, is_purchased=True)

    if location_id is not None:
        query = query.filter_by(location_id=location_id)  

    plants = query.order_by(Plant.created_at.desc()).all()  

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

# ACHTUNG: VORERST DIESE ROUTE NICHT MEHR VERWENDEN!!! STATTDESSEN /api/recommendations
@app.route('/api/plants', methods=['GET'])
def list_all_plants():
    '''
    ALT: Kombinierte Gesamtübersicht:
    - Wunschliste
    - Bestand
    - Empfehlungen aus PlantCatalog

    Wird aktuell NICHT vom Frontend verwendet
    '''
    user_id, err = require_login()
    if err:
        return err

    location_id = request.args.get("location_id", type=int)

    selected_location = None
    if location_id is not None:
        selected_location = Location.query.filter_by(id=location_id, user_id=user_id).first()
        if not selected_location:
            return jsonify({"error": "Standort nicht gefunden"}), 404

    # 1. User-Pflanzen laden
    user_query = Plant.query.filter_by(user_id=user_id)

    if location_id is not None:
        user_query = user_query.filter_by(location_id=location_id)

    user_plants = user_query.order_by(Plant.created_at.desc()).all()

    result = []

    for p in user_plants:
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
            "created_at": str(p.created_at),
            "source": "inventory" if p.is_purchased else "wishlist"
        })

    # 2. Bereits vorhandene Pflanzen ausschließen
    #    (Wunschliste + Bestand)
    all_owned_plants = Plant.query.filter_by(user_id=user_id).all()
    owned_plant_keys = {get_plant_identity(p) for p in all_owned_plants}

    # Bereits vorhandene Bestands-Pflanzen für ästhetischen Vergleich
    inventory_plants = Plant.query.filter_by(user_id=user_id, is_purchased=True).all()

    if selected_location is not None:
        inventory_plants_at_location = Plant.query.filter_by(
            user_id=user_id,
            is_purchased=True,
            location_id=location_id
        ).all()
    else:
        inventory_plants_at_location = inventory_plants

    # 3. Empfehlungen aus PlantCatalog
    catalog_plants = PlantCatalog.query.order_by(PlantCatalog.name.asc()).all()

    recommendation_items = []

    for catalog_plant in catalog_plants:
        # Keine Pflanze empfehlen, die schon vorhanden ist
        if get_plant_identity(catalog_plant) in owned_plant_keys:
            continue

        suitability = None
        suitability_checks = []
        aesthetic_bonus = 0
        aesthetic_reasons = []

        # Wenn ein Standort gewählt ist:
        # nur geeignete oder bedingt geeignete Empfehlungen anzeigen
        if selected_location is not None:
            suitability_result = check_plant_location_suitability(catalog_plant, selected_location)

            if suitability_result["suitability"] not in ["geeignet", "bedingt geeignet"]:
                continue

            suitability = suitability_result["suitability"]
            suitability_checks = suitability_result["checks"]

            aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(
                catalog_plant,
                inventory_plants_at_location
            )
        else:
            # Ohne Standort: nur allgemeine Empfehlung ohne Standortprüfung
            aesthetic_bonus, aesthetic_reasons = calculate_aesthetic_bonus(
                catalog_plant,
                inventory_plants
            )

        recommendation_items.append({
            "id": catalog_plant.id,
            "name": catalog_plant.name,
            "botanical_name": catalog_plant.botanical_name,
            "is_purchased": False,
            "location_id": location_id if selected_location is not None else None,
            "location_name": selected_location.name if selected_location is not None else None,
            "light_requirement": catalog_plant.light_requirement,
            "water_requirement": catalog_plant.water_requirement,
            "temperature_requirement": catalog_plant.temperature_requirement,
            "humidity_requirement": catalog_plant.humidity_requirement,
            "soil_type": catalog_plant.soil_type,
            "height_min": catalog_plant.height_min,
            "height_max": catalog_plant.height_max,
            "poisonous": bool(catalog_plant.poisonous),
            "flowering_season_start": catalog_plant.flowering_season_start,
            "flowering_season_end": catalog_plant.flowering_season_end,
            "flower_color": catalog_plant.flower_color,
            "notes": None,
            "created_at": str(catalog_plant.created_at),
            "source": "recommendation",
            "suitability": suitability,
            "checks": suitability_checks,
            "aesthetic_bonus": aesthetic_bonus,
            "aesthetic_reasons": aesthetic_reasons
        })

    # Empfehlungen sortieren:
    # geeignet vor bedingt geeignet, dann höherer Bonus, dann alphabetisch
    suitability_order = {
        None: 2,
        "geeignet": 0,
        "bedingt geeignet": 1
    }

    recommendation_items.sort(
        key=lambda r: (
            suitability_order.get(r["suitability"], 99),
            -r["aesthetic_bonus"],
            r["name"].lower()
        )
    )

    result.extend(recommendation_items)

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
            return jsonify({"error": err}), 400
        plant.light_requirement = data.get("light_requirement")

    if "water_requirement" in data:
        ok, err = validate_enum("water_requirement", data.get("water_requirement"), ALLOWED_WATER)
        if not ok:
            return jsonify({"error": err}), 400
        plant.water_requirement = data.get("water_requirement")

    if "humidity_requirement" in data:
        ok, err = validate_enum("humidity_requirement", data.get("humidity_requirement"), ALLOWED_HUMIDITY)
        if not ok:
            return jsonify({"error": err}), 400
        plant.humidity_requirement = data.get("humidity_requirement")

    if "temperature_requirement" in data:
        ok, err = validate_enum("temperature_requirement",
                                data.get("temperature_requirement"),
                                ALLOWED_TEMP)
        if not ok:
            return jsonify({"error": err}), 400

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

@app.route('/locations/create', methods=['POST'])
def create_location_form():
    '''
    neuen Standort anlegen
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    name = request.form.get('name')

    if not name:
        locations = get_user_locations(user_id)
        return render_template(
            'standorte.html',
            username=session['username'],
            locations=locations,
            error="Name darf nicht leer sein"
        )

    try:
        new_location = Location(
            name=name,
            user_id=user_id
        )

        db.session.add(new_location)
        db.session.commit()

        return redirect(url_for('locations_page'))

    except Exception as e:
        db.session.rollback()
        locations = get_user_locations(user_id)
        return render_template(
            'standorte.html',
            username=session['username'],
            locations=locations,
            error=f"Fehler beim Erstellen: {str(e)}"
        )

@app.route('/locations/<int:location_id>/update', methods=['POST'])
def update_location(location_id):
    '''
    Standort bearbeiten und speichern
    '''
    if 'username' not in session:
        return redirect(url_for('auth'))

    user_id = session['user_id']

    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=None,
            error="Standort nicht gefunden"
        )

    name = request.form.get('name')
    lighting_condition = request.form.get('lighting_condition')
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')
    description = request.form.get('description')

    location_data = {
        "id": location.id,
        "name": name,
        "lighting_condition": lighting_condition,
        "temperature": temperature,
        "humidity": humidity,
        "description": description
    }

    if not name:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=location_data,
            error="Name darf nicht leer sein"
        )

    ok, err = validate_enum("lighting_condition", lighting_condition, ALLOWED_LIGHT)
    if not ok:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=location_data,
            error=err
        )

    ok, err = validate_enum("temperature", temperature, ALLOWED_TEMP)
    if not ok:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=location_data,
            error=err
        )

    ok, err = validate_enum("humidity", humidity, ALLOWED_HUMIDITY)
    if not ok:
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=location_data,
            error=err
        )

    try:
        location.name = name
        location.lighting_condition = lighting_condition or None
        location.temperature = temperature or None
        location.humidity = humidity or None
        location.description = description

        db.session.commit()

        return redirect(url_for('locations_page'))

    except Exception as e:
        db.session.rollback()
        return render_template(
            'aendern_standort.html',
            username=session['username'],
            location=location_data,
            error=f"Fehler beim Speichern: {str(e)}"
        )
# App starten
if __name__ == '__main__':
    app.run(debug=True)
