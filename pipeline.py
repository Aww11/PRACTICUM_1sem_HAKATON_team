import pandas as pd

from src.collectors.cbr import (
    fetch_required_reserves,
    fetch_ruonia,
    fetch_ruonia_avg,
    fetch_repo_auctions,
    fetch_key_rate,
    fetch_bliquidity,
)
from src.collectors.minfin import fetch_ofz_auctions
from src.collectors.fns import fetch_tax_calendar
from src.collectors.roskazna import fetch_treasury_deposits
from src.modules.m1_reserves import compute_m1
from src.modules.m2_repo import compute_m2
from src.modules.m3_ofz import compute_m3
from src.modules.m4_tax import compute_m4
from src.modules.m5_treasury import compute_m5
from src.agg.lsi import build_lsi


def _log_df(name, df_):
    print("\n==", name, "==")
    print("shape:", df_.shape)
    print("columns:", df_.columns.tolist())
    print(df_.head(3).to_string() if not df_.empty else df_.to_string())


def run_pipeline():
    reserves = fetch_required_reserves()
    ruonia = fetch_ruonia()
    ruonia_avg = fetch_ruonia_avg()
    repo = fetch_repo_auctions()
    key_rate = fetch_key_rate()
    ofz = fetch_ofz_auctions()
    tax = fetch_tax_calendar()
    treasury = fetch_treasury_deposits()
    _ = fetch_bliquidity()

    for name, df_ in [
        ("reserves", reserves),
        ("ruonia", ruonia),
        ("ruonia_avg", ruonia_avg),
        ("repo", repo),
        ("key_rate", key_rate),
        ("ofz", ofz),
        ("tax", tax),
        ("treasury", treasury),
    ]:
        _log_df(name, df_)

    m1 = compute_m1(reserves, ruonia) if not reserves.empty and not ruonia.empty else pd.DataFrame()
    m2 = compute_m2(repo, key_rate) if not repo.empty and not key_rate.empty else pd.DataFrame()
    m3 = compute_m3(ofz) if not ofz.empty else pd.DataFrame()
    m4 = compute_m4(tax) if not tax.empty else pd.DataFrame()
    m5 = compute_m5(treasury) if not treasury.empty else pd.DataFrame()

    for name, df_ in [("m1", m1), ("m2", m2), ("m3", m3), ("m4", m4), ("m5", m5)]:
        _log_df(name, df_)

    frames = [df for df in [m1, m2, m3, m4, m5] if not df.empty]
    if not frames:
        return pd.DataFrame()

    df = frames[0]
    for other in frames[1:]:
        df = df.merge(other, on="date", how="outer")

    df = df.sort_values("date").reset_index(drop=True)
    df = build_lsi(df)
    return df


if __name__ == "__main__":
    df = run_pipeline()
    if not df.empty:
        df.to_csv("output/lsi_output.csv", index=False)
        print("saved output/lsi_output.csv")