import pandas as pd
import numpy as np
from dateutil import parser as dparser
import argparse


def parse_time(x):
    try:
        return dparser.parse(x)
    except Exception:
        return pd.NaT


def haversine_distance(row):
    """Compute great-circle distance between pickup and dropoff coordinates (km)."""
    if any(
        pd.isna(v)
        for v in [
            row.pickup_latitude,
            row.pickup_longitude,
            row.dropoff_latitude,
            row.dropoff_longitude,
        ]
    ):
        return np.nan
    R = 6371 
    lat1, lon1, lat2, lon2 = map(
        np.radians,
        [
            row.pickup_latitude,
            row.pickup_longitude,
            row.dropoff_latitude,
            row.dropoff_longitude,
        ],
    )
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to cleaned CSV")
    ap.add_argument("--out_csv", required=True, help="Path to write updated CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    print(f"Loaded {len(df):,} rows")

    if "duration_sec" not in df.columns or df["duration_sec"].isna().all():
        df["pickup_dt"] = pd.to_datetime(
            df["pickup_datetime"].apply(parse_time), errors="coerce"
        )
        df["dropoff_dt"] = pd.to_datetime(
            df["dropoff_datetime"].apply(parse_time), errors="coerce"
        )
        df["duration_sec"] = (df["dropoff_dt"] - df["pickup_dt"]).dt.total_seconds()
        df.loc[df["duration_sec"] <= 0, "duration_sec"] = np.nan

    missing_distance = df["trip_distance"].isna() | (df["trip_distance"] <= 0)
    df.loc[missing_distance, "distance_km_est"] = df.loc[missing_distance].apply(
        haversine_distance, axis=1
    )
    df.loc[missing_distance, "trip_distance"] = (
        df.loc[missing_distance, "distance_km_est"] / 1.60934
    )

    km = df["trip_distance"] * 1.60934
    df["speed_kmh"] = km / (df["duration_sec"] / 3600)
    df.loc[(df["speed_kmh"] <= 0) | (df["speed_kmh"] > 200), "speed_kmh"] = np.nan

    df["fare_per_km"] = df["fare_amount"] / km
    df.loc[(df["fare_per_km"] <= 0) | (df["fare_per_km"] > 50), "fare_per_km"] = np.nan

    df.to_csv(args.out_csv, index=False)
    print(f"✅ Updated dataset saved to {args.out_csv}")


if __name__ == "__main__":
    main()