import pandas as pd


def compute_m1(reserves: pd.DataFrame, ruonia: pd.DataFrame) -> pd.DataFrame:
    if reserves is None or ruonia is None or reserves.empty or ruonia.empty:
        return pd.DataFrame()

    r = reserves.copy()
    u = ruonia.copy()

    r["date"] = pd.to_datetime(r["date"], errors="coerce").dt.normalize()
    u["date"] = pd.to_datetime(u["date"], errors="coerce").dt.normalize()

    if "required_reserves" not in r.columns or "ruonia" not in u.columns:
        return pd.DataFrame()

    out = r.merge(u, on="date", how="outer")
    out["m1_signal"] = pd.to_numeric(out["required_reserves"], errors="coerce") - pd.to_numeric(out["ruonia"], errors="coerce")
    out = out[["date", "m1_signal"]].sort_values("date").reset_index(drop=True)
    return out