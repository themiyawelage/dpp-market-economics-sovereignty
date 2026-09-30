import math

import numpy as np


def finite(values):
    return np.array([float(v) for v in values if v is not None and np.isfinite(float(v))], dtype=float)


def summary(values):
    x = finite(values)
    if len(x) == 0:
        return {"n": 0, "mean": None, "sd": None, "median": None, "min": None, "max": None}
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "sd": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
        "median": float(np.median(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
    }


def zscore(x):
    x = np.asarray(x, dtype=float)
    sd = np.std(x, ddof=0)
    return np.zeros_like(x) if sd == 0 else (x - np.mean(x)) / sd


def safe_log1p(value):
    if value is None:
        return None
    value = float(value)
    return math.log1p(max(value, 0.0))
