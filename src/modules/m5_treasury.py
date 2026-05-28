import pandas as pd


def compute_m5(treasury: pd.DataFrame) -> pd.DataFrame:
    if treasury is None or treasury.empty:
        return pd.DataFrame()

    df = treasury.copy()
    if "date" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()

    num_cols = [c for c in df.columns if c != "date"]
    if not num_cols:
        return pd.DataFrame()

    val_col = num_cols[0]
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce")
    df = df.dropna(subset=["date", val_col])

    if df.empty:
        return pd.DataFrame()

    out = (
        df.groupby("date")[val_col]
        .sum()
        .reset_index(name="m5_signal")
        .sort_values("date")
        .reset_index(drop=True)
    )
    return out