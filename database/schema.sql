-- Datenbankschema 

-- Tabelle für Standorte
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    lighting_condition TEXT CHECK(lighting_condition IN ('schatten', 'halbschatten', 'sonnig')),
    temperature TEXT CHECK(temperature IN ('kalt', 'kuehl', 'warm')),
    humidity TEXT CHECK(humidity IN ('trocken', 'normal', 'feucht')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle für Pflanzen
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    botanical_name TEXT,

    -- Standortanforderungen
    light_requirement TEXT CHECK(light_requirement IN ('schatten', 'halbschatten', 'sonnig')),
    water_requirement TEXT CHECK(water_requirement IN ('wenig', 'mittel', 'viel')),
    temperature_min INTEGER,
    temperature_max INTEGER,
    humidity_requirement TEXT CHECK(humidity_requirement IN ('trocken', 'normal', 'feucht')),
    soil_type TEXT,

    -- Eigenschaften
    height_min INTEGER, -- in cm
    height_max INTEGER, -- in cm
    poisonous BOOLEAN DEFAULT 0,
    flowering_season_start INTEGER, -- Monat (1-12)
    flowering_season_end INTEGER,   -- Monat (1-12)
    flower_color TEXT,

    -- Status
    is_purchased BOOLEAN DEFAULT 0,
    location_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_plants_location ON plants(location_id);
CREATE INDEX IF NOT EXISTS idx_plants_purchased ON plants(is_purchased);