import pandas as pd


def compute_m3(ofz: pd.DataFrame) -> pd.DataFrame:
    if ofz is None or ofz.empty:
        return pd.DataFrame()

    df = ofz.copy()
    if "date" not in df.columns:
        df["date"] = pd.NaT

    if "title" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()

    if df["date"].isna().all():
        df["date"] = pd.Timestamp.today().normalize()

    out = (
        df.groupby("date")
        .size()
        .reset_index(name="m3_signal")
        .sort_values("date")
        .reset_index(drop=True)
    )
    return out