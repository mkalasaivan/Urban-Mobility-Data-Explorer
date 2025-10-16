"""
Manual Median Absolute Deviation (MAD)-based anomaly detection
No numpy, no pandas.sort_values. Pure Python.

We flag trips with unusually high speed_kmh based on robust z-scores.
"""

def _manual_median(values):
    # Copy list to avoid mutating caller data
    arr = list(values)
    # Manual insertion sort (stable, O(n^2), sufficient for per-request slices)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    n = len(arr)
    if n == 0:
        return None
    mid = n // 2
    if n % 2 == 1:
        return arr[mid]
    else:
        return (arr[mid-1] + arr[mid]) / 2.0

def robust_zscores(values):
    """
    Compute robust z-scores via MAD.
    z_i = 0.6745 * (x_i - median) / MAD
    Where MAD = median(|x_i - median|).
    Returns list of floats (or None if insufficient data).
    """
    n = len(values)
    if n < 5:
        return [0.0 for _ in values]  # too small to judge

    med = _manual_median(values)
    abs_dev = [abs(x - med) for x in values]
    mad = _manual_median(abs_dev)
    if mad is None or mad == 0:
        return [0.0 for _ in values]
    factor = 0.6745 / mad
    return [factor * (x - med) for x in values]

def flag_anomalies(values, threshold=3.5):
    """
    Return indices where |z| >= threshold.
    """
    zs = robust_zscores(values)
    return [i for i, z in enumerate(zs) if abs(z) >= threshold]
