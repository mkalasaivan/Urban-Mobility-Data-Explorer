import argparse, csv, json
from dateutil import parser as dparser
import pandas as pd

from algorithms.mad_anomaly import flag_anomalies

def parse_time(x):
    try:
        return dparser.parse(x)
    except Exception:
        return None

def sec_delta(a, b):
    return int((b - a).total_seconds()) if (a and b) else None

def kmh(distance_miles, seconds):
    if distance_miles is None or seconds is None or seconds <= 0:
        return None
    km = distance_miles * 1.60934
    hours = seconds / 3600.0
    return km / hours if hours > 0 else None

def fare_per_km(fare, distance_miles):
    if fare is None or distance_miles is None or distance_miles <= 0:
        return None
    km = distance_miles * 1.60934
    return fare / km if km > 0 else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to raw NYC taxi CSV")
    ap.add_argument("--out_csv", required=True, help="Path to write cleaned CSV")
    ap.add_argument("--log", required=True, help="Path to write cleaning log JSON")
    args = ap.parse_args()

    log = {"rows_total": 0, "rows_clean": 0, "excluded": []}
    clean_rows = []

    # Stream with pandas for speed but keep algorithmic parts manual where needed
    # (You may switch to csv module if memory is constrained and process in chunks)
    df = pd.read_csv(args.input, low_memory=False)

    # Normalize column names (edit these if your CSV differs)
    colmap = {
        "pickup_datetime": "pickup_datetime",
        "dropoff_datetime": "dropoff_datetime",
        "pickup_longitude": "pickup_longitude",
        "pickup_latitude": "pickup_latitude",
        "dropoff_longitude": "dropoff_longitude",
        "dropoff_latitude": "dropoff_latitude",
        "trip_distance": "trip_distance",
        "fare_amount": "fare_amount",
        "tip_amount": "tip_amount",
        "payment_type": "payment_type",
        "passenger_count": "passenger_count",
        "PULocationID": "pickup_zone",
        "DOLocationID": "dropoff_zone"
    }

    # Create missing columns if not present
    for c in colmap:
        if c not in df.columns:
            df[c] = None

    log["rows_total"] = len(df)

    # Basic cleaning
    df["pickup_dt"] = df["pickup_datetime"].apply(parse_time)
    df["dropoff_dt"] = df["dropoff_datetime"].apply(parse_time)
    df["duration_sec"] = df.apply(lambda r: sec_delta(r["pickup_dt"], r["dropoff_dt"]), axis=1)

    # Derived features
    df["speed_kmh"] = df.apply(lambda r: kmh(r["trip_distance"], r["duration_sec"]), axis=1)
    df["fare_per_km"] = df.apply(lambda r: fare_per_km(r["fare_amount"], r["trip_distance"]), axis=1)

    # Exclusion rules
    reasons = []
    # invalid times or negative/zero durations
    reasons.append(("bad_time", ~(df["duration_sec"].notna() & (df["duration_sec"] > 0))))
    # impossible speeds > 200 km/h
    reasons.append(("speed_impossible", df["speed_kmh"].notna() & (df["speed_kmh"] > 200)))
    # negative fares or distances
    reasons.append(("neg_values", (df["fare_amount"].fillna(0) < 0) | (df["trip_distance"].fillna(0) < 0)))

    exclude_mask = False
    for name, mask in reasons:
        df.loc[mask, "exclude_reason"] = name
        exclude_mask = mask if exclude_mask is False else (exclude_mask | mask)

    # Manual MAD-based anomaly on speed (robust)
    speeds = df.loc[~exclude_mask & df["speed_kmh"].notna(), "speed_kmh"].tolist()
    idxs = flag_anomalies(speeds, threshold=5.0)  # stricter threshold for heavy tails
    # Mark those specific rows as suspicious (not excluded by default; logged)
    df["suspicious"] = False
    good_speeds = df.loc[~exclude_mask & df["speed_kmh"].notna(), :].copy()
    if len(idxs) > 0:
        suspicious_indices = good_speeds.iloc[idxs].index
        df.loc[suspicious_indices, "suspicious"] = True

    # Build cleaned frame
    clean_df = df.loc[~exclude_mask, [
        "pickup_datetime","dropoff_datetime",
        "pickup_longitude","pickup_latitude",
        "dropoff_longitude","dropoff_latitude",
        "trip_distance","duration_sec",
        "fare_amount","tip_amount",
        "fare_per_km","speed_kmh",
        "payment_type","passenger_count",
        "PULocationID","DOLocationID","suspicious"
    ]].copy()

    clean_df.rename(columns={
        "PULocationID":"pickup_zone",
        "DOLocationID":"dropoff_zone"
    }, inplace=True)

    log["rows_clean"] = len(clean_df)
    # Record excluded sample counts
    excl_counts = df["exclude_reason"].value_counts(dropna=True).to_dict()
    log["excluded"] = [{"reason": k, "count": int(v)} for k, v in excl_counts.items()]

    # Write outputs
    clean_df.to_csv(args.out_csv, index=False)

    with open(args.log, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print(f"Done. Clean rows: {log['rows_clean']} / {log['rows_total']}")
    print(f"Log written to {args.log}")

if __name__ == "__main__":
    main()
