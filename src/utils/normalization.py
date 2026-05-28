import numpy as np
import pandas as pd

def mad_score(series: pd.Series, window: int = 756) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    med = x.rolling(window, min_periods=max(20, window // 10)).median()
    mad = (x - med).abs().rolling(window, min_periods=max(20, window // 10)).median()
    denom = 1.4826 * mad.replace(0, np.nan)
    return (x - med) / denom

def robust_minmax(series: pd.Series, lower: float = 1, upper: float = 99) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    lo = x.quantile(lower / 100)
    hi = x.quantile(upper / 100)
    return ((x - lo) / (hi - lo)).clip(0, 1)