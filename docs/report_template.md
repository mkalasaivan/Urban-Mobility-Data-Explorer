# NYC Mobility Insights — Technical Report (Template)

## 1) Problem Framing & Dataset Analysis
- **Dataset**: NYC Taxi Trip (raw trip-level). Columns used: pickup/dropoff times, coordinates, distance, fare, tip, payment, passenger, PULocationID/DOLocationID.
- **Challenges**:
  - Messy timestamps, invalid coordinates, zero/negative durations
  - Outliers: impossible speeds, negative fares/distances
  - Heterogeneous columns across files
- **Assumptions**:
  - Distances are in miles (converted to km for derived metrics)
  - Missing zones allowed but excluded from zone rankings
- **Unexpected Observation** (example to validate with your data):
  - Night-time trips show higher average speed but not always lower fare/km — suggests congestion not the only driver of fare efficiency.

## 2) System Architecture & Design Decisions
```mermaid
flowchart LR
  A[Raw CSV] -->|process.py| B[(SQLite DB)]
  B <--> C[Flask API]
  C --> D[Frontend Dashboard (HTML/JS)]
```
- **Stack**: Python (Flask) + SQLite for simplicity and portability.
- **Schema**: normalized single fact table for trips (see `schema.sql`) with indexes on pickup time & zones.
- **Trade-offs**:
  - SQLite chosen for speed of setup; Postgres recommended for concurrency.
  - Manual DSA implementations to satisfy grading rubric vs using optimized libs.

## 3) Algorithmic Logic & Data Structures
- **Manual MAD Anomaly Detection** (see code):
  - Pseudocode + complexity included inline.
  - Flags high-`speed_kmh` outliers using robust z-scores.
- **Manual Top‑K Frequent Pickup Zones**:
  - Frequency map + iterative max selection (no Counter/heapq).
  - Returns top‑K zones for dashboard.

## 4) Insights & Interpretation (Examples – replace with your results)
1. **Rush-Hour Slowdown**: 7–9am and 4–7pm show lower speed_kmh and higher fare/km.
   - Evidence: `/api/summary/metrics` segmented by hour; chart screenshot.
   - Interpretation: congestion pricing or route choice affects efficiency.
2. **Airport Gravity**: Top pickup zones include airport-adjacent tracts.
   - Evidence: `/api/summary/top-pickups?k=10`.
   - Interpretation: mobility demand clusters at hubs.
3. **Anomalies at Night**: A small set of trips exhibit extreme speeds.
   - Evidence: `/api/insights/anomalies` with robust z-score ≥ 3.5.
   - Interpretation: data quality issues or highway segments.

## 5) Reflection & Future Work
- **Challenges**: inconsistent columns across files; tuning outlier thresholds; front-end time aggregation.
- **Next Steps**:
  - Move to Postgres with partitioning & spatial indexes
  - Add map-based visualization (Leaflet)
  - Deploy with Docker + Nginx reverse-proxy
