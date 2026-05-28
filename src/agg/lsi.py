import pandas as pd
import numpy as np

DEFAULT_WEIGHTS = {"m1": 0.25, "m2": 0.20, "m3": 0.20, "m4": 0.10, "m5": 0.25}


def _scale_series(x: pd.Series) -> pd.Series:
    x = pd.to_numeric(x, errors="coerce")
    if x.notna().sum() == 0:
        return pd.Series(np.nan, index=x.index, dtype="float64")
    x = x.fillna(x.median())
    lo = x.quantile(0.05)
    hi = x.quantile(0.95)
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(np.nan, index=x.index, dtype="float64")
    return ((x - lo) / (hi - lo)).clip(0, 1)


def build_lsi(df: pd.DataFrame, weights: dict = DEFAULT_WEIGHTS) -> pd.DataFrame:
    out = df.copy()
    score = pd.Series(0.0, index=out.index, dtype="float64")
    used = 0

    for k, w in weights.items():
        if k in out.columns:
            x = _scale_series(out[k])
            if x.notna().any():
                score = score + x.fillna(x.median()) * w
                used += 1

    if used == 0:
        out["lsi"] = np.nan
        out["status"] = "Neutral / Insufficient data"
        out["data_quality"] = "NO_SIGNAL"
        return out

    if score.isna().all() or score.max() == score.min():
        out["lsi"] = np.nan
        out["status"] = "Neutral / Insufficient data"
        out["data_quality"] = "INSUFFICIENT_VARIANCE"
        return out

    out["lsi"] = 100 * (score - score.min()) / (score.max() - score.min())
    out["lsi"] = out["lsi"].clip(0, 100)
    out["status"] = pd.cut(
        out["lsi"],
        bins=[-1, 40, 70, 100],
        labels=["GREEN", "YELLOW", "RED"],
    )
    out["data_quality"] = "OK"
    return out