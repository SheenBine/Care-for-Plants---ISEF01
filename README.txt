INSTALLATIONS- UND START-ANLEITUNG 

SCHRITT 1: Projekt klonen/downloaden
-------------------------------------
- Das Projektverzeichnis auf deinen Computer kopieren oder klonen

SCHRITT 2: Python-Umgebung vorbereiten
---------------------------------------
Öffne die Kommandozeile im Projektverzeichnis und führe aus:

    python -m venv venv

Aktiviere die virtuelle Umgebung:
- Windows (CMD): venv\Scripts\activate
- Windows (PowerShell): venv\Scripts\Activate.ps1
- Mac/Linux: source venv/bin/activate

SCHRITT 3: Abhängigkeiten installieren
---------------------------------------
Mit aktivierter virtueller Umgebung:

    pip install -r requirements.txt

SCHRITT 4: App starten
----------------------
Starte die Flask-App im Terminal:

    python app.py

Die App sollte nun auf http://localhost:5000 laufen

SCHRITT 5: Browser öffnen
--------------------------
Öffne einen Browser und gehe zu:

    http://localhost:5000/

SCHRITT 6: Testuser verwenden
------------------------------
Du kannst dich mit folgenden Credentials einloggen:

    Benutzername: testuser
    Passwort: 1234

Der Testuser wird automatisch beim ersten Start angelegt!

Hinweis: Das Passwort ist sicher gehasht in der Datenbank gespeichert und dient nur für die Demo.


TROUBLESHOOTING
===============
- Falls die Datenbank nicht erstellt wird: Stelle sicher, dass der "database/" Ordner existiert
- Falls "ModuleNotFoundError": Stelle sicher, dass alle Abhängigkeiten installiert sind (pip install -r requirements.txt)
- Falls Port 5000 bereits belegt ist: Die App sollte automatisch einen anderen Port wählen oder starte sie mit: python app.py --port=5001