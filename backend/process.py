import argparse, json, math
import pandas as pd
import numpy as np
from dateutil import parser as dparser
from algorithms.mad_anomaly import flag_anomalies


# ---------- Utility Functions ----------

def parse_time(x):
    try:
        return dparser.parse(x)
    except Exception:
        return pd.NaT


def estimate_fare(distance_miles, duration_sec):
    """Estimate fare if missing using approximate NYC taxi rates."""
    base_fare = 2.5
    per_km_rate = 0.5
    per_min_rate = 0.35
    km = distance_miles * 1.60934
    mins = duration_sec / 60
    return np.round(base_fare + per_km_rate * km + per_min_rate * mins, 2)


# ---------- Main Cleaning ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to raw NYC taxi CSV")
    ap.add_argument("--out_csv", required=True, help="Path to write cleaned CSV")
    ap.add_argument("--log", required=True, help="Path to write cleaning log JSON")
    args = ap.parse_args()

    log = {"rows_total": 0, "rows_clean": 0, "excluded": []}
    df = pd.read_csv(args.input, low_memory=False)
    log["rows_total"] = len(df)

    # Ensure required columns exist
    req_cols = [
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "trip_distance",
        "fare_amount",
        "tip_amount",
        "payment_type",
        "passenger_count",
        "PULocationID",
        "DOLocationID",
    ]
    for c in req_cols:
        if c not in df.columns:
            df[c] = np.nan

    # ---------- Datetime Conversion ----------
    df["pickup_dt"] = pd.to_datetime(
        df["pickup_datetime"].apply(parse_time), errors="coerce"
    )
    df["dropoff_dt"] = pd.to_datetime(
        df["dropoff_datetime"].apply(parse_time), errors="coerce"
    )

    df["duration_sec"] = (df["dropoff_dt"] - df["pickup_dt"]).dt.total_seconds()
    df.loc[df["duration_sec"] <= 0, "duration_sec"] = np.nan

    # ---------- Haversine Distance (Vectorized) ----------
    R = 6371  # Earth radius km
    lat1 = np.radians(df["pickup_latitude"])
    lat2 = np.radians(df["dropoff_latitude"])
    dlon = np.radians(df["dropoff_longitude"] - df["pickup_longitude"])
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    df["distance_km_est"] = R * c

    # Fill missing or invalid trip distances (convert to miles)
    mask_missing = df["trip_distance"].isna() | (df["trip_distance"] <= 0)
    df.loc[mask_missing, "trip_distance"] = (
        df.loc[mask_missing, "distance_km_est"] / 1.60934
    )

    # ---------- Estimate Missing Fares ----------
    mask_fare_missing = df["fare_amount"].isna() | (df["fare_amount"] <= 0)
    df.loc[mask_fare_missing, "fare_amount"] = estimate_fare(
        df.loc[mask_fare_missing, "trip_distance"].fillna(0),
        df.loc[mask_fare_missing, "duration_sec"].fillna(0),
    )

    # ---------- Derived Features ----------
    km = df["trip_distance"] * 1.60934
    df["speed_kmh"] = km / (df["duration_sec"] / 3600)
    df.loc[df["speed_kmh"] <= 0, "speed_kmh"] = np.nan

    df["fare_per_km"] = df["fare_amount"] / km
    df.loc[df["fare_per_km"] <= 0, "fare_per_km"] = np.nan

    # ---------- Exclusion Rules ----------
    reasons = {}
    mask_bad_time = df["duration_sec"].isna()
    reasons["bad_time"] = int(mask_bad_time.sum())

    mask_speed_high = df["speed_kmh"].notna() & (df["speed_kmh"] > 200)
    reasons["speed_impossible"] = int(mask_speed_high.sum())

    mask_neg_values = (df["fare_amount"] < 0) | (df["trip_distance"] < 0)
    reasons["neg_values"] = int(mask_neg_values.sum())

    # ✅ Combine all invalid conditions
    exclude_mask = mask_bad_time | mask_speed_high | mask_neg_values

    df["exclude_reason"] = np.select(
        [mask_bad_time, mask_speed_high, mask_neg_values],
        ["bad_time", "speed_impossible", "neg_values"],
        default=None
    ).astype("object")

    # ---------- Anomaly Detection (MAD) ----------
    speeds = df.loc[~exclude_mask & df["speed_kmh"].notna(), "speed_kmh"].to_list()
    idxs = flag_anomalies(speeds, threshold=5.0)
    df["suspicious"] = False
    if len(idxs) > 0:
        valid_index = df.loc[~exclude_mask & df["speed_kmh"].notna()].iloc[idxs].index
        df.loc[valid_index, "suspicious"] = True

    # ---------- Final Clean Dataset ----------
    clean_df = df.loc[
        ~exclude_mask,
        [
            "pickup_datetime",
            "dropoff_datetime",
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude",
            "trip_distance",
            "duration_sec",
            "fare_amount",
            "tip_amount",
            "fare_per_km",
            "speed_kmh",
            "payment_type",
            "passenger_count",
            "PULocationID",
            "DOLocationID",
            "suspicious",
        ],
    ].copy()

    clean_df.rename(
        columns={"PULocationID": "pickup_zone", "DOLocationID": "dropoff_zone"},
        inplace=True,
    )

    log["rows_clean"] = len(clean_df)
    log["excluded"] = [{"reason": k, "count": v} for k, v in reasons.items()]

    clean_df.to_csv(args.out_csv, index=False)
    with open(args.log, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print(f"✅ Done. Clean rows: {log['rows_clean']} / {log['rows_total']}")
    print(f"📝 Log written to {args.log}")


if __name__ == "__main__":
    main()
