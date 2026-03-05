# Datenbankmodelle
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Datenbank wird in app.py importiert und mit Flask verbunden
db = SQLAlchemy()

class User(db.Model):
    '''
    Usermodell für Authentifizierung
    - id: Primärschlüssel
    - username: eindeutiger Name des Benutzers
    - password_hash: sicher gespeicherter Hash des Passworts
    '''
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        '''
        Passwort setzen.
        Hasht das Passwort, damit es nicht in Klartext gespeichert wird.
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''
        Prüft, ob ein Klartext-Passwort zum gespeicherten Hash passt.
        Gibt True zurück, sonst False.
        '''
        return check_password_hash(self.password_hash, password)
    
class Location(db.Model):
    '''
    Standortmodell
    - id: Primärschlüssel
    - user_id: gehört zu einem User
    - name: Name des Standorts
    - lighting_condition / temperature / humidity: Enum-Strings
    '''
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    lighting_condition = db.Column(db.String(20))   # schatten, halbschatten, sonnig
    temperature = db.Column(db.String(20))          # kalt, normal, warm
    humidity = db.Column(db.String(20))             # trocken, normal, feucht
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

class Plant(db.Model):
    '''
    Pflanzenmodell
    - user_id: Pflanzen pro User speichern
    - is_purchased: False = Wunschliste, True = gekauft/bestand
    - location_id: kann nach Kauf gesetzt werden
    '''
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)

    # pro User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    botanical_name = db.Column(db.String(200))

    # Standortanforderungen
    light_requirement = db.Column(db.String(20))      # schatten, halbschatten, sonnig
    water_requirement = db.Column(db.String(20))      # wenig, mittel, viel
    temperature_requirement = db.Column(db.String(20))
    humidity_requirement = db.Column(db.String(20))   # trocken, normal, feucht
    soil_type = db.Column(db.String(120))

    # Eigenschaften
    height_min = db.Column(db.Integer)                
    height_max = db.Column(db.Integer)                
    poisonous = db.Column(db.Boolean, default=False)
    flowering_season_start = db.Column(db.Integer)    
    flowering_season_end = db.Column(db.Integer)      
    flower_color = db.Column(db.String(80))

    # Status
    is_purchased = db.Column(db.Boolean, default=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())