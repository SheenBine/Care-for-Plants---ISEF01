CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    lighting_condition TEXT CHECK(lighting_condition IN ('schatten', 'halbschatten', 'sonnig')),
    temperature TEXT CHECK(temperature IN ('kalt', 'normal', 'warm')),
    humidity TEXT CHECK(humidity IN ('trocken', 'normal', 'feucht')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    botanical_name TEXT,

    light_requirement TEXT CHECK(light_requirement IN ('schatten', 'halbschatten', 'sonnig')),
    water_requirement TEXT CHECK(water_requirement IN ('wenig', 'mittel', 'viel')),
    temperature_min INTEGER,
    temperature_max INTEGER,
    humidity_requirement TEXT CHECK(humidity_requirement IN ('trocken', 'normal', 'feucht')),
    soil_type TEXT,

    height_min INTEGER, 
    height_max INTEGER, 
    poisonous BOOLEAN DEFAULT 0,
    flowering_season_start INTEGER, 
    flowering_season_end INTEGER,   
    flower_color TEXT,

    is_purchased BOOLEAN DEFAULT 0,
    location_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plant_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    score REAL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plant_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    botanical_name TEXT,

    light_requirement TEXT CHECK(light_requirement IN ('schatten', 'halbschatten', 'sonnig')),
    water_requirement TEXT CHECK(water_requirement IN ('wenig', 'mittel', 'viel')),
    temperature_requirement TEXT CHECK(temperature_requirement IN ('kalt', 'normal', 'warm')),
    humidity_requirement TEXT CHECK(humidity_requirement IN ('trocken', 'normal', 'feucht')),
    soil_type TEXT,

    height_min INTEGER,
    height_max INTEGER,
    flower_color TEXT,
    poisonous BOOLEAN DEFAULT 0,
    flowering_season_start INTEGER CHECK(flowering_season_start BETWEEN 1 AND 12),
    flowering_season_end INTEGER CHECK(flowering_season_end BETWEEN 1 AND 12),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_plants_location ON plants(location_id);
CREATE INDEX IF NOT EXISTS idx_plants_purchased ON plants(is_purchased);
CREATE INDEX IF NOT EXISTS idx_locations_user ON locations(user_id);
CREATE INDEX IF NOT EXISTS idx_plants_user ON plants(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_location ON recommendations(location_id);