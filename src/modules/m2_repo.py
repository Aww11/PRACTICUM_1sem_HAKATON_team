import pandas as pd

def compute_m2(repo: pd.DataFrame, key_rate: pd.DataFrame) -> pd.DataFrame:
    repo = repo.copy()
    key_rate = key_rate.copy()

    if "date" not in repo.columns:
        repo["date"] = pd.to_datetime(repo.iloc[:, 0], errors="coerce")
    else:
        repo["date"] = pd.to_datetime(repo["date"], errors="coerce")

    if "Date" in key_rate.columns:
        key_rate["date"] = pd.to_datetime(key_rate["Date"], dayfirst=True, errors="coerce")
    elif "date" in key_rate.columns:
        key_rate["date"] = pd.to_datetime(key_rate["date"], dayfirst=True, errors="coerce")
    else:
        key_rate["date"] = pd.NaT

    repo["date"] = repo["date"].dt.normalize()
    key_rate["date"] = key_rate["date"].dt.normalize()

    repo = repo.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    key_rate = key_rate.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")

    if "cover_ratio" not in repo.columns:
        if repo.shape[1] > 1:
            repo["cover_ratio"] = pd.to_numeric(repo.iloc[:, 1], errors="coerce")
        else:
            repo["cover_ratio"] = pd.NA
    else:
        repo["cover_ratio"] = pd.to_numeric(repo["cover_ratio"], errors="coerce")

    if "rate_spread" not in repo.columns:
        repo["rate_spread"] = pd.NA
    else:
        repo["rate_spread"] = pd.to_numeric(repo["rate_spread"], errors="coerce")

    if "Rate" in key_rate.columns:
        kr = key_rate[["date", "Rate"]].rename(columns={"Rate": "key_rate"})
    elif "key_rate" in key_rate.columns:
        kr = key_rate[["date", "key_rate"]].copy()
    else:
        if key_rate.shape[1] > 1:
            kr = key_rate.iloc[:, :2].copy()
            kr.columns = ["date", "key_rate"]
        else:
            kr = key_rate[["date"]].copy()
            kr["key_rate"] = pd.NA

    df = repo[["date", "cover_ratio", "rate_spread"]].merge(kr, on="date", how="outer")

    df["cover_ratio"] = pd.to_numeric(df["cover_ratio"], errors="coerce")
    df["rate_spread"] = pd.to_numeric(df["rate_spread"], errors="coerce")
    df["key_rate"] = pd.to_numeric(df["key_rate"], errors="coerce")

    df["mad_cover"] = df["cover_ratio"].rolling(3, min_periods=1).median()
    df["mad_rate_spread"] = df["rate_spread"].rolling(3, min_periods=1).median()
    df["flag_demand"] = ((df["cover_ratio"] < 1.2) & (df["rate_spread"] > 0)).astype(int)

    return df[["date", "cover_ratio", "rate_spread", "mad_cover", "mad_rate_spread", "flag_demand"]]