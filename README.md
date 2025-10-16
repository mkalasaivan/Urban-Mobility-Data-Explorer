# NYC Mobility Insights — Full‑Stack Application

This project is a **complete full‑stack data analytics platform** for exploring and visualizing **New York City Taxi Trip data**.  
It integrates a **Flask API**, **SQLite database**, and **interactive JavaScript dashboard** to deliver powerful insights about urban mobility.

---

## 🚀 Quick Start (Local Setup)

### 0️⃣ Prerequisites
- Python 3.10+
- Node not required (pure HTML/JS frontend)
- Install dependencies:
```bash
pip install -r requirements.txt
```

### 1️⃣ Prepare Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Process & Load Data
Place your raw NYC taxi CSV file in the `data/` directory (e.g., `data/train.csv`), then clean and load it into the database:

```bash
python backend/process.py --input data/train.csv --out_csv data/clean_trips.csv --log data/clean_log.json
python backend/load.py --csv data/clean_trips.csv --db db/nyc.sqlite
```

### 3️⃣ Run the Application
```bash
export FLASK_APP=backend/app.py
flask run
```
The API will start at **http://127.0.0.1:5000**.

### 4️⃣ Open the Dashboard
Open `frontend/index.html` in your browser.  
It connects automatically to the Flask API at **http://127.0.0.1:5000**.

---

## 🐳 Run with Docker (Recommended)

Run the entire project — **backend**, **database**, and **frontend** — inside a single Docker container.

### 1️⃣ Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2️⃣ Build the Image
```bash
docker compose build
```

### 3️⃣ Start the Container
```bash
docker compose up
```

Visit the app in your browser:  
👉 **http://127.0.0.1:5000**

✅ Both the Flask backend and the web dashboard will be running inside Docker.

### 4️⃣ Stop the Container
```bash
docker compose down
```

### 5️⃣ Verify API Health
```bash
curl http://127.0.0.1:5000/api/health
```
Expected output:
```json
{"status": "ok"}
```

---

## 📂 Project Structure

```
backend/
  app.py
  process.py
  load.py
  algorithms/
    mad_anomaly.py
    topk_manual.py
frontend/
  index.html
  app.js
  styles.css
db/
  nyc.sqlite
data/
  clean_trips.csv
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

## 🔍 API Endpoints

| Endpoint | Description |
|-----------|--------------|
| `/api/health` | Health check |
| `/api/trips?start=&end=&limit=&offset=` | Fetch trip data |
| `/api/summary/metrics` | Summary metrics (average speed, fare/km, total fare) |
| `/api/summary/top-pickups?k=10` | Top pickup zones (custom Top‑K algorithm) |
| `/api/insights/anomalies` | Speed anomalies (custom MAD algorithm) |

---

## ⚙️ Algorithms Implemented Manually

- **Median Absolute Deviation (MAD)** — detects anomalies without using built‑in sorting or median functions.  
- **Top‑K Frequent Zones** — finds most common pickup zones using a manual frequency selection method (no `Counter`, `heapq`, or built‑in sort).

Both algorithms are implemented from scratch and include pseudocode, explanations, and complexity analysis.

---

## 🧠 Key Features

- Full data pipeline: cleaning → feature engineering → database → analytics API → interactive dashboard  
- Responsive web UI with visual summaries and insights  
- Modular, documented Python backend with custom algorithms  
- Lightweight and deployable anywhere using Docker  

---

## 🧰 Useful Docker Commands

| Command | Description |
|----------|-------------|
| `docker compose build` | Build or rebuild the image |
| `docker compose up` | Start the container |
| `docker compose down` | Stop and remove containers |
| `docker ps` | List running containers |
| `docker logs nyc_mobility_app` | View application logs |

---

## 💡 Notes

- The frontend is served directly by Flask — no separate web server is needed.  
- The SQLite database in `db/` is mounted as a persistent volume, so your data remains intact after restarts.  
- If you change source files, rebuild with `docker compose up --build` to apply updates.  
- You can open a shell in the container with:
  ```bash
  docker exec -it nyc_mobility_app bash
  ```

---

## ✨ Authors
Developed by **Isaac Habumugisha**, **Kalasa Ivan**, and team  
Built for analyzing real‑world **urban mobility patterns** in New York City.
