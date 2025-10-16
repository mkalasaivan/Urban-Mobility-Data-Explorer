from flask import Flask, request, jsonify, send_from_directory
import sqlite3, os
from flask_cors import CORS
from algorithms.topk_manual import topk_frequent
from algorithms.mad_anomaly import robust_zscores

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "nyc.sqlite")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")

app = Flask(__name__)  
CORS(app)

def get_conn():
    return sqlite3.connect(DB_PATH)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

def date_filters(params):
    start = params.get("start")
    end = params.get("end")
    where = []
    args = []
    if start:
        where.append("pickup_datetime >= ?")
        args.append(start)
    if end:
        where.append("pickup_datetime <= ?")
        args.append(end)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    return clause, args

@app.get("/api/trips")
def trips():
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    clause, args = date_filters(request.args)

    fields = "pickup_datetime, dropoff_datetime, pickup_zone, dropoff_zone, trip_distance, duration_sec, fare_amount, tip_amount, fare_per_km, speed_kmh"
    sql = f"SELECT {fields} FROM trips{clause} ORDER BY pickup_datetime LIMIT ? OFFSET ?"
    args2 = args + [limit, offset]

    conn = get_conn()
    rows = conn.execute(sql, args2).fetchall()
    conn.close()

    cols = [c.strip() for c in fields.split(",")]
    data = [dict(zip(cols, r)) for r in rows]
    return jsonify(data)

@app.get("/api/summary/metrics")
def metrics():
    clause, args = date_filters(request.args)
    conn = get_conn()
    row = conn.execute(f"""
        SELECT
            COUNT(*) as n,
            AVG(speed_kmh) as avg_speed,
            AVG(fare_per_km) as avg_fpkm,
            SUM(fare_amount) as total_fare
        FROM trips{clause}
    """, args).fetchone()
    conn.close()
    return jsonify({
        "trips": row[0] or 0,
        "avg_speed_kmh": round(row[1], 2) if row[1] is not None else None,
        "avg_fare_per_km": round(row[2], 2) if row[2] is not None else None,
        "total_fare": round(row[3], 2) if row[3] is not None else None
    })

@app.get("/api/summary/top-pickups")
def top_pickups():
    k = int(request.args.get("k", 10))
    clause, args = date_filters(request.args)
    conn = get_conn()
    rows = conn.execute(f"SELECT pickup_zone FROM trips{clause}", args).fetchall()
    conn.close()
    zones = [r[0] for r in rows if r[0] is not None]
    topk = topk_frequent(zones, k)
    return jsonify([{"zone": z, "count": int(c)} for z, c in topk])

@app.get("/api/insights/anomalies")
def anomalies():
    # Return trips whose speed robust z-score exceeds threshold
    threshold = float(request.args.get("z", 3.5))
    clause, args = date_filters(request.args)
    conn = get_conn()
    rows = conn.execute(f"SELECT rowid, speed_kmh FROM trips{clause}", args).fetchall()
    conn.close()

    speeds = [r[1] for r in rows if r[1] is not None]
    ids = [r[0] for r in rows if r[1] is not None]

    zs = robust_zscores(speeds)
    flagged = []
    for i, z in enumerate(zs):
        if abs(z) >= threshold:
            flagged.append({"rowid": ids[i], "speed_kmh": speeds[i], "z": z})
    return jsonify(flagged[:500])  # cap

if __name__ == "__main__":
    app.run(debug=True)
    from flask import send_from_directory




@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(FRONTEND_DIR, path)
