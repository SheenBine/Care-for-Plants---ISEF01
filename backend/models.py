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
