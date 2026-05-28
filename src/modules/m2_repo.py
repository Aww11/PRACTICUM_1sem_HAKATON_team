import pandas as pd


def compute_m2(repo: pd.DataFrame, key_rate: pd.DataFrame) -> pd.DataFrame:
    if repo is None or key_rate is None:
        return pd.DataFrame()

    if repo.empty or key_rate.empty:
        return pd.DataFrame()

    r = repo.copy()
    k = key_rate.copy()

    r["metric"] = r["metric"].astype(str).str.strip().str.lower()
    r["value"] = pd.to_numeric(r["value"], errors="coerce")
    r["date"] = pd.to_datetime(r["date"], errors="coerce").dt.normalize()

    k["date"] = pd.to_datetime(k["date"], errors="coerce").dt.normalize()
    k["key_rate"] = pd.to_numeric(k["key_rate"], errors="coerce")

    r = r.dropna(subset=["date", "value"])
    k = k.dropna(subset=["date", "key_rate"]).sort_values("date")

    bids = r[r["metric"].str.contains("total bids received", na=False)][["date", "value"]].rename(
        columns={"value": "total_bids"}
    )
    allotted = r[r["metric"].str.contains("total amount allotted", na=False)][["date", "value"]].rename(
        columns={"value": "total_allotted"}
    )
    cutoff = r[
        r["metric"].str.contains("cut-off rate", na=False)
        | r["metric"].str.contains("cut off rate", na=False)
    ][["date", "value"]].rename(columns={"value": "cut_off_rate"})

    df = bids.merge(allotted, on="date", how="outer")
    df = df.merge(cutoff, on="date", how="outer")
    df = df.sort_values("date").reset_index(drop=True)

    if df.empty:
        return pd.DataFrame()

    df = pd.merge_asof(
        df.sort_values("date"),
        k[["date", "key_rate"]].sort_values("date"),
        on="date",
        direction="backward",
    )

    df["cover_ratio"] = df["total_bids"] / df["total_allotted"]
    df["rate_spread"] = df["cut_off_rate"] - df["key_rate"]

    df["mad_cover"] = df["cover_ratio"].rolling(window=3, min_periods=1).mean()
    df["mad_rate_spread"] = df["rate_spread"].rolling(window=3, min_periods=1).mean()

    df["flag_demand"] = (
        (df["cover_ratio"].fillna(0) > 1.0)
        & (df["rate_spread"].fillna(0) >= 0)
    ).astype(int)

    out = df[["date", "cover_ratio", "rate_spread", "mad_cover", "mad_rate_spread", "flag_demand"]].copy()
    out = out.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    return out