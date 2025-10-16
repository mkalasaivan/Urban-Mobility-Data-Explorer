import argparse, sqlite3, csv, os

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Cleaned/enriched trips CSV")
    ap.add_argument("--db", required=True, help="SQLite path to create/populate")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.db), exist_ok=True)
    conn = sqlite3.connect(args.db)

    # Run schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    rows = 0

    print(f"📂 Loading {args.csv} into {args.db} ...")

    with open(args.csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            cur.execute(
                """
                INSERT INTO trips (
                    pickup_datetime, dropoff_datetime,
                    pickup_longitude, pickup_latitude,
                    dropoff_longitude, dropoff_latitude,
                    trip_distance, duration_sec,
                    fare_amount, tip_amount,
                    fare_per_km, speed_kmh,
                    payment_type, passenger_count,
                    pickup_zone, dropoff_zone
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    r.get("pickup_datetime"),
                    r.get("dropoff_datetime"),
                    _to_float(r.get("pickup_longitude")),
                    _to_float(r.get("pickup_latitude")),
                    _to_float(r.get("dropoff_longitude")),
                    _to_float(r.get("dropoff_latitude")),
                    _to_float(r.get("trip_distance")),
                    _to_int(r.get("duration_sec")),
                    _to_float(r.get("fare_amount")),
                    _to_float(r.get("tip_amount")),
                    _to_float(r.get("fare_per_km")),
                    _to_float(r.get("speed_kmh")),
                    r.get("payment_type"),
                    _to_int(r.get("passenger_count")),
                    str(r.get("pickup_zone")) if r.get("pickup_zone") else None,
                    str(r.get("dropoff_zone")) if r.get("dropoff_zone") else None,
                ),
            )
            rows += 1
            if rows % 10000 == 0:
                conn.commit()
                print(f"   ✅ Inserted {rows:,} rows...")

    conn.commit()
    conn.close()
    print(f"✅ All done — inserted {rows:,} rows into database.")


def _to_float(x):
    try:
        return float(x) if x not in (None, "", "NaN") else None
    except Exception:
        return None


def _to_int(x):
    try:
        return int(float(x)) if x not in (None, "", "NaN") else None
    except Exception:
        return None


if __name__ == "__main__":
    main()