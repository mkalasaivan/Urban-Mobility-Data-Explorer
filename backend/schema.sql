
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY,
    pickup_datetime TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,
    pickup_longitude REAL,
    pickup_latitude REAL,
    dropoff_longitude REAL,
    dropoff_latitude REAL,
    trip_distance REAL,
    duration_sec INTEGER,
    fare_amount REAL,
    tip_amount REAL,
    fare_per_km REAL,
    speed_kmh REAL,
    payment_type TEXT,
    passenger_count INTEGER,
    pickup_zone TEXT,
    dropoff_zone TEXT
);

CREATE INDEX IF NOT EXISTS idx_trips_pickup_dt ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_zone ON trips(pickup_zone);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_zone ON trips(dropoff_zone);
