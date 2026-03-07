# Care for Plants – Backend-Routen Übersicht (für Frontend)

Backend läuft lokal unter:
`http://127.0.0.1:5000`

Diese Übersicht zeigt **welche API im Frontend für welche Seite verwendet werden soll**.

---

# Wunschliste

Seite:
`/wishlist`

API zum Laden der Daten:

GET
`/api/wishlist`

Pflanze hinzufügen:

POST
`/api/wishlist`

Pflanze löschen:

DELETE
`/api/wishlist/<plant_id>`

---

# Bestand

Seite:
`/inventory`

API zum Laden:

GET
`/api/inventory`

Pflanze direkt zum Bestand hinzufügen:

POST
`/api/inventory`

Pflanze bearbeiten / verschieben:

PATCH
`/api/plants/<plant_id>`

---

# Standorte

Seite:
`/locations`

Standorte laden:

GET
`/api/locations`

Standort erstellen:

POST
`/api/locations`

Standort löschen:

DELETE
`/api/locations/<location_id>`

---

# Pflanzen eines Standorts

Seite:
`/locations/<location_id>/plants`

API zum Laden:

GET
`/api/locations/<location_id>/plants`

---

# Gesamtübersicht aller Pflanzen

Seite:
`/plants`

API:

GET
`/api/plants`

---

# Pflanze bearbeiten

Seite:
`/plants/<plant_id>/edit`

API zum Speichern:

PATCH
`/api/plants/<plant_id>`

---

# Standort bearbeiten

Seite:
`/locations/<location_id>/edit`

API zum Speichern:

PATCH
`/api/locations/<location_id>` *(falls später ergänzt)*

---

# Standortprüfung (Standortvorschläge)

API:

GET
`/api/plants/<plant_id>/check-location/<location_id>`

Prüft ob eine Pflanze zu einem Standort passt.

---

# Pflanzenempfehlungen

API:

GET
`/api/locations/<location_id>/recommend-plants`

Gibt passende Pflanzen aus dem **Pflanzenkatalog** zurück.

---

# Wichtig für das Frontend

Alle API-Routen geben **JSON** zurück.

Die Seiten (`/wishlist`, `/inventory`, usw.) laden nur das **HTML-Template**.
Die eigentlichen Daten müssen über die **API-Routen mit fetch() oder axios geladen werden.**
