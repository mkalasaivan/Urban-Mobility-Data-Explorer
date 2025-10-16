# === Stage 1: build environment ===
FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Copy backend and requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything needed (backend, frontend, db)
COPY backend/ backend/
COPY frontend/ frontend/
COPY db/ db/

# Environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PORT=5000

# Expose Flask port
EXPOSE 5000

# Run Flask (serving both API + static frontend)
CMD ["flask", "run"]
