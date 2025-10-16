# NYC Mobility Insights — Full‑Stack App (Starter Kit)

This repository is a **complete, runnable starter** for your summative assignment using the **NYC Taxi Trip dataset**.
It gives you a **working Flask API + SQLite DB + vanilla JS dashboard**, plus **data processing scripts** and a
**custom algorithms module (no Counter/heapq/sort_values)** to satisfy the DSA requirement.

> ✅ You must supply the official raw dataset (`train.zip` or CSVs) yourself. This starter **does not** include data.

---

## Quick Start (Local)

### 0) Prereqs
- Python 3.10+
- Node not required (pure HTML/JS frontend)
- `pip install -r requirements.txt`

### 1) Prepare environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Process & load data
Place your raw CSV (from the official NYC taxi dataset) somewhere, e.g., `data/train.csv`.
Then run the processing script — it will clean data, engineer features, log exclusions, and build an SQLite DB.

```bash
python backend/process.py --input data/train.csv --out_csv data/clean_trips.csv --log data/clean_log.json
python backend/load.py --csv data/clean_trips.csv --db db/nyc.sqlite
```

### 3) Run API
```bash
export FLASK_APP=backend/app.py
flask run
# API will start on http://127.0.0.1:5000
```

### 4) Open the dashboard
Open `frontend/index.html` in your browser (or serve with a simple static server). It talks to `http://127.0.0.1:5000`.

> Tip: If you host the frontend separately, set `API_BASE` at the top of `frontend/app.js`.

---

## Project Structure

```
backend/
  app.py                # Flask API
  process.py            # Data cleaning & feature engineering
  load.py               # DB loader
  schema.sql            # SQLite schema (created automatically as needed)
  algorithms/
    mad_anomaly.py      # Median Absolute Deviation (manual) for outlier detection
    topk_manual.py      # Manual top-K using simple selection (no Counter/heapq)
db/
  (nyc.sqlite)          # Created after load
frontend/
  index.html
  app.js
  styles.css
docs/
  report_template.md    # 2–3 page documentation template
  architecture.mmd      # Mermaid architecture diagram (render in Markdown previewers)
scripts/
  seed.sh               # Example one-liner
requirements.txt
README.md
```

---

## API Overview

- `GET /api/health` → `{status:"ok"}`
- `GET /api/trips?start=YYYY-MM-DD&end=YYYY-MM-DD&limit=100&offset=0`
- `GET /api/summary/metrics?start=...&end=...` → totals, avg speed, avg fare/km, etc.
- `GET /api/summary/top-pickups?k=10&start=...&end=...` → uses **manual top‑K** algo
- `GET /api/insights/anomalies?start=...&end=...` → detects speed outliers via **manual MAD**

All endpoints support date filtering by pickup time.

---

## DSA Requirement (Manual Implementations)

- **Median Absolute Deviation (MAD)**: computes robust z‑scores to flag anomalies. Implemented **from scratch** with manual median and absolute deviations — **no** `numpy.median`, **no** `pandas.sort_values`.
- **Top‑K Frequent Pickup Zones**: custom frequency map with a **manual selection routine** (no `Counter.most_common`, no `heapq`, no built-in sorting for the result).

Each module contains:
- Explanation
- Pseudocode
- Time/space complexity

See `backend/algorithms/mad_anomaly.py` and `backend/algorithms/topk_manual.py`.

---

## Documentation

Use `docs/report_template.md` to draft your 2–3 page write‑up.
Export to PDF for submission.

The `docs/architecture.mmd` file contains a Mermaid diagram you can embed in your report or README previews.

---

## Notes

- This starter reads **raw CSV** and expects columns like `pickup_datetime`, `dropoff_datetime`, `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, `dropoff_latitude`, `trip_distance`, `fare_amount`, `tip_amount`.
  If your raw file uses different column names, edit `process.py` mappings.
- All cleaning decisions and exclusions are logged to `--log` for transparency.
- Indexes on time and location support efficient queries.

Good luck — and tell a compelling story about how the city moves!
