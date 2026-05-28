import pandas as pd

EPISODES = [
    ("2014-12-01", "2014-12-31"),
    ("2022-02-01", "2022-03-31"),
    ("2023-08-01", "2023-08-31"),
]

def run_backtest(df: pd.DataFrame, episodes=EPISODES) -> pd.DataFrame:
    rows = []
    for start, end in episodes:
        mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
        part = df.loc[mask].copy()
        if part.empty:
            rows.append({
                "start": start,
                "end": end,
                "max_lsi": pd.NA,
                "mean_lsi": pd.NA,
                "red_days": 0,
                "note": "no data in period",
            })
        else:
            rows.append({
                "start": start,
                "end": end,
                "max_lsi": part["lsi"].max(),
                "mean_lsi": part["lsi"].mean(),
                "red_days": int((part["status"] == "RED").sum()),
                "note": "",
            })
    return pd.DataFrame(rows)