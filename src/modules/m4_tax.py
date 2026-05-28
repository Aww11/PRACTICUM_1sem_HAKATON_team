import pandas as pd


def compute_m4(tax: pd.DataFrame) -> pd.DataFrame:
    if tax is None or tax.empty:
        return pd.DataFrame()

    df = tax.copy()
    if "date" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["date"])

    if df.empty:
        return pd.DataFrame()

    out = (
        df.groupby("date")
        .size()
        .reset_index(name="m4_signal")
        .sort_values("date")
        .reset_index(drop=True)
    )
    return out