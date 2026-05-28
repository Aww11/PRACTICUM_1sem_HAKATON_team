import pandas as pd

def compute_m1(reserves: pd.DataFrame, ruonia: pd.DataFrame) -> pd.DataFrame:
    if ruonia is None or ruonia.empty:
        return pd.DataFrame()

    u = ruonia.copy()
    u["date"] = pd.to_datetime(u["date"], errors="coerce").dt.normalize()
    u["ruonia"] = pd.to_numeric(u["ruonia"], errors="coerce")
    u = u.dropna(subset=["date", "ruonia"]).sort_values("date").reset_index(drop=True)

    if u.empty:
        return pd.DataFrame()

    if reserves is not None and not reserves.empty and "date" in reserves.columns:
        r = reserves.copy()
        r["date"] = pd.to_datetime(r["date"], errors="coerce").dt.normalize()
        if "required_reserves" in r.columns:
            r["required_reserves"] = pd.to_numeric(r["required_reserves"], errors="coerce")
            r = r.dropna(subset=["date"]).sort_values("date")
            df = r.merge(u, on="date", how="outer")
            df["m1_signal"] = df["required_reserves"] - df["ruonia"]
            return df[["date", "m1_signal"]].dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    print("m1_reserves loaded")
    print("ruonia rows:", len(ruonia) if ruonia is not None else None)
    print("reserves empty:", reserves.empty if reserves is not None else None)

    u["ruonia_ma3"] = u["ruonia"].rolling(window=3, min_periods=1).mean()
    u["m1_signal"] = u["ruonia"] - u["ruonia_ma3"]
    return u[["date", "m1_signal"]].sort_values("date").reset_index(drop=True)