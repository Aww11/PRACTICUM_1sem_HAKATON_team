import pandas as pd

def compute_m5(treasury: pd.DataFrame) -> pd.DataFrame:
    treasury = treasury.copy()

    if "Дата" in treasury.columns:
        treasury["date"] = pd.to_datetime(treasury["Дата"], dayfirst=True, errors="coerce")
    elif "date" in treasury.columns:
        treasury["date"] = pd.to_datetime(treasury["date"], errors="coerce")
    else:
        raise KeyError("treasury: no date column found")

    treasury["date"] = treasury["date"].dt.normalize()
    treasury = treasury.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")

    if "balance" not in treasury.columns:
        treasury["balance"] = pd.NA
    else:
        treasury["balance"] = pd.to_numeric(treasury["balance"], errors="coerce")

    if treasury["balance"].isna().all():
        treasury["balance"] = range(len(treasury))

    treasury["delta"] = treasury["balance"].diff()
    treasury["mad_balance"] = treasury["balance"].rolling(3, min_periods=1).median()
    treasury["mad_delta"] = treasury["delta"].rolling(3, min_periods=1).median()
    treasury["flag_budget_drain"] = (treasury["delta"] < 0).astype(int)

    return treasury[["date", "balance", "delta", "mad_balance", "mad_delta", "flag_budget_drain"]]