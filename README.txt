INSTALLATIONS- UND STARTANLEITUNG
================================

1. Projekt herunterladen oder klonen
------------------------------------
Das Projektverzeichnis lokal auf den Rechner kopieren oder per Git klonen.

2. Virtuelle Umgebung anlegen
-----------------------------
Im Projektverzeichnis im Terminal ausführen:

    python -m venv venv

3. Virtuelle Umgebung aktivieren
--------------------------------
Windows (PowerShell):

    venv\Scripts\Activate.ps1

Mac/Linux:

    source venv/bin/activate

4. Abhängigkeiten installieren
------------------------------
Mit aktivierter virtueller Umgebung ausführen:

    pip install -r requirements.txt

5. Anwendung starten
--------------------
Im Projektverzeichnis ausführen:

    python app.py

6. Anwendung im Browser öffnen
------------------------------
Die Anwendung ist anschließend erreichbar unter:

    http://localhost:5000/

7. Testzugang
-------------
Beim ersten Start werden automatisch Demo-Daten angelegt, sofern die Datenbank leer ist.

Testbenutzer:
    Benutzername: testuser
    Passwort: 1234

Zusätzlich werden automatisch Beispielstandorte, Beispielpflanzen und Einträge
für den Pflanzenkatalog erzeugt.

PROJEKTSTRUKTUR
===============
Wichtige Dateien und Ordner:

- app.py
  Zentrale Flask-Anwendung mit HTML-Routen, API-Routen, Validierung,
  Geschäftslogik und Initialisierungslogik

- models.py
  SQLAlchemy-Modelle für Benutzer, Standorte, Pflanzen und Pflanzenkatalog

- templates/
  HTML-Templates für die Benutzeroberfläche

- static/css/
  CSS-Dateien für das Layout und Design

- database/database.db
  SQLite-Datenbank der Anwendung

- requirements.txt
  Python-Abhängigkeiten des Projekts

TECHNISCHE HINWEISE
===================
- Die Anwendung verwendet Flask als Webframework.
- Die Daten werden in einer SQLite-Datenbank gespeichert.
- Passwörter werden nicht im Klartext gespeichert, sondern gehasht.
- HTML-Seiten werden serverseitig über Flask-Templates gerendert.
- Zusätzlich stellt die Anwendung JSON-API-Endpunkte bereit.

TROUBLESHOOTING
===============
- Falls die Datenbank nicht erstellt wird:
  Prüfen, ob der Ordner "database/" vorhanden ist.

- Falls Module fehlen:
  Sicherstellen, dass die virtuelle Umgebung aktiviert ist und die
  Abhängigkeiten mit `pip install -r requirements.txt` installiert wurden.

- Falls Port 5000 bereits belegt ist:
  Die belegende Anwendung beenden oder Flask lokal mit angepasster
  Konfiguration starten.