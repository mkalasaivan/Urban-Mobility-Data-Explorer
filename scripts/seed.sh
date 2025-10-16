#!/usr/bin/env bash
set -e
python backend/process.py --input "$1" --out_csv data/clean_trips.csv --log data/clean_log.json
python backend/load.py --csv data/clean_trips.csv --db db/nyc.sqlite
FLASK_APP=backend/app.py flask run
