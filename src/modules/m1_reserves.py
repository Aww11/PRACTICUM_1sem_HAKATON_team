import pandas as pd

def compute_m1(reserves: pd.DataFrame, ruonia: pd.DataFrame) -> pd.DataFrame:
    reserves = reserves.copy()
    ruonia = ruonia.copy()

    if "Averaging Period Starting on" in reserves.columns:
        reserves["date"] = pd.to_datetime(reserves["Averaging Period Starting on"], dayfirst=True, errors="coerce")
    elif "date" in reserves.columns:
        reserves["date"] = pd.to_datetime(reserves["date"], dayfirst=True, errors="coerce")
    else:
        raise KeyError("reserves: no date column found")

    if "date" not in ruonia.columns:
        if "Date of rate" in ruonia.columns:
            ruonia["date"] = pd.to_datetime(ruonia["Date of rate"], dayfirst=True, errors="coerce")
        elif "Date" in ruonia.columns:
            ruonia["date"] = pd.to_datetime(ruonia["Date"], dayfirst=True, errors="coerce")
        else:
            raise KeyError("ruonia: no date column found")
    else:
        ruonia["date"] = pd.to_datetime(ruonia["date"], dayfirst=True, errors="coerce")

    reserves["date"] = reserves["date"].dt.normalize()
    ruonia["date"] = ruonia["date"].dt.normalize()

    reserves = reserves.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    ruonia = ruonia.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")

    rr_col = "Required Reserves to be Averaged on Correspondent Accounts2"
    if rr_col not in reserves.columns:
        rr_col = reserves.columns[-2]

    if "RUONIA, % p.a." in ruonia.columns:
        ruonia_col = "RUONIA, % p.a."
    elif "ruonia" in ruonia.columns:
        ruonia_col = "ruonia"
    else:
        ruonia_col = ruonia.columns[1]

    df = reserves[["date", rr_col]].merge(
        ruonia[["date", ruonia_col]],
        on="date",
        how="outer"
    )

    df = df.rename(columns={
        rr_col: "required_reserves",
        ruonia_col: "ruonia"
    })

    df["required_reserves"] = pd.to_numeric(df["required_reserves"], errors="coerce")
    df["ruonia"] = pd.to_numeric(df["ruonia"], errors="coerce")

    df["spread"] = df["required_reserves"] - df["ruonia"]
    df["mad_spread"] = df["spread"].rolling(3, min_periods=1).median()
    df["mad_ruonia"] = df["ruonia"].rolling(3, min_periods=1).median()
    df["flag_end_period"] = 0

    return df[["date", "required_reserves", "ruonia", "spread", "mad_spread", "mad_ruonia", "flag_end_period"]]