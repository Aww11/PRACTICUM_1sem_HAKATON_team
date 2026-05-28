import pandas as pd
import numpy as np


def _robust_scale(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    valid = s.dropna()
    if valid.empty:
        return s * np.nan
    med = valid.median()
    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return (s - med).fillna(0.0)
    return ((s - med) / iqr).replace([np.inf, -np.inf], np.nan)


def build_lsi(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.normalize()

    weights = {
        "m1_signal": 0.30,
        "flag_demand": 0.40,
        "m5_signal": 0.15,
        "m3_signal": 0.10,
        "m4_signal": 0.05,
    }

    feature_frames = []
    used_weights = []
    present_cols = []

    for col, w in weights.items():
        if col not in out.columns:
            continue
        s = out[col]
        if col == "flag_demand":
            feat = pd.to_numeric(s, errors="coerce").fillna(0.0)
        else:
            feat = _robust_scale(s).fillna(0.0)
        feature_frames.append(feat * w)
        used_weights.append(w)
        present_cols.append(col)

    if not feature_frames:
        out["lsi"] = np.nan
        out["status"] = "Neutral / Insufficient data"
        out["data_quality"] = "NO_SIGNAL"
        out["data_quality_score"] = 0.0
        return out

    weighted = pd.concat(feature_frames, axis=1)
    denom = sum(used_weights)

    out["lsi_raw"] = weighted.sum(axis=1) / max(denom, 1e-9)
    out["lsi"] = 1 / (1 + np.exp(-out["lsi_raw"]))

    out["data_quality_score"] = out[present_cols].notna().sum(axis=1) / len(weights)
    out["data_quality"] = np.where(
        out[present_cols].notna().sum(axis=1) > 0,
        "PARTIAL_SIGNAL",
        "NO_SIGNAL",
    )

    out["status"] = np.where(
        out["lsi"] > 0.6,
        "Positive / Partial data",
        np.where(
            out["lsi"] < 0.4,
            "Negative / Partial data",
            "Neutral / Partial data",
        ),
    )

    keep = [
        "date",
        "m1_signal",
        "cover_ratio",
        "rate_spread",
        "mad_cover",
        "mad_rate_spread",
        "flag_demand",
        "m3_signal",
        "m4_signal",
        "m5_signal",
        "lsi_raw",
        "lsi",
        "status",
        "data_quality",
        "data_quality_score",
    ]
    keep = [c for c in keep if c in out.columns]
    return out[keep].sort_values("date").reset_index(drop=True)