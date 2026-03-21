# Datenbankmodelle
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Datenbank wird in app.py importiert und mit Flask verbunden
db = SQLAlchemy()


class User(db.Model):
    '''
    Benutzerkonto für Login und Registrierung
    '''
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        '''
        Speichert das Passwort als Hash
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''
        Prüft ein Passwort gegen den gespeicherten Hash
        '''
        return check_password_hash(self.password_hash, password)


class Location(db.Model):
    '''
    Benutzerbezogener Standort für Pflanzen
    '''
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    lighting_condition = db.Column(db.String(20))
    temperature = db.Column(db.String(20))
    humidity = db.Column(db.String(20))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


class Plant(db.Model):
    '''
    Benutzerbezogene Pflanze für Wunschliste oder Bestand
    '''
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    botanical_name = db.Column(db.String(200))

    light_requirement = db.Column(db.String(20))
    water_requirement = db.Column(db.String(20))
    temperature_requirement = db.Column(db.String(20))
    humidity_requirement = db.Column(db.String(20))
    soil_type = db.Column(db.String(120))

    height_min = db.Column(db.Integer)
    height_max = db.Column(db.Integer)
    poisonous = db.Column(db.Boolean, default=False)
    flowering_season_start = db.Column(db.Integer)
    flowering_season_end = db.Column(db.Integer)
    flower_color = db.Column(db.String(80))

    is_purchased = db.Column(db.Boolean, default=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


class PlantCatalog(db.Model):
    '''
    Allgemeiner Pflanzenkatalog für Empfehlungen
    '''
    __tablename__ = "plant_catalog"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    botanical_name = db.Column(db.String(200))

    light_requirement = db.Column(db.String(20))
    water_requirement = db.Column(db.String(20))
    temperature_requirement = db.Column(db.String(20))
    humidity_requirement = db.Column(db.String(20))
    soil_type = db.Column(db.String(120))

    height_min = db.Column(db.Integer)
    height_max = db.Column(db.Integer)
    flower_color = db.Column(db.String(80))
    poisonous = db.Column(db.Boolean, default=False)

    flowering_season_start = db.Column(db.Integer)
    flowering_season_end = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())