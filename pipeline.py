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
        print("\n==", name, "==")
        print("shape:", df_.shape)
        print("columns:", df_.columns.tolist())
        print(df_.head(3).to_string())

    if any(x.empty for x in [reserves, ruonia, repo, key_rate, ofz, tax, treasury]):
        return pd.DataFrame()

    m1 = compute_m1(reserves, ruonia)
    m2 = compute_m2(repo, key_rate)
    m3 = compute_m3(ofz)
    m4 = compute_m4(tax)
    m5 = compute_m5(treasury)

    for name, df_ in [("m1", m1), ("m2", m2), ("m3", m3), ("m4", m4), ("m5", m5)]:
        print("\n==", name, "==")
        print("shape:", df_.shape)
        print("columns:", df_.columns.tolist())
        print(df_.head(3).to_string())

    df = m1.merge(m2, on="date", how="outer", indicator=True)
    print("\nmerge m1+m2:", df["_merge"].value_counts(dropna=False).to_dict())
    df = df.drop(columns=["_merge"])

    df = df.merge(m3, on="date", how="outer")
    df = df.merge(m4, on="date", how="outer")
    df = df.merge(m5, on="date", how="outer")

    df = df.sort_values("date").reset_index(drop=True)
    df = build_lsi(df)
    return df


if __name__ == "__main__":
    df = run_pipeline()
    if not df.empty:
        df.to_csv("output/lsi_output.csv", index=False)
        print("saved output/lsi_output.csv")