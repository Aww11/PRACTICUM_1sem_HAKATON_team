import pandas as pd
from src.backtest.backtest import run_backtest

df = pd.read_csv("output/lsi_output.csv", parse_dates=["date"])
bt = run_backtest(df)
bt.to_csv("output/backtest.csv", index=False)
print(bt.to_string(index=False))