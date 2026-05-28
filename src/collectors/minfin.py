import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def fetch_ofz_auctions():
    url = "https://minfin.gov.ru/en/policy_issues/debt/domestic/operations/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception:
        return pd.DataFrame()

    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a")
    rows = []

    for a in links:
        text = " ".join(a.get_text(" ", strip=True).split())
        href = a.get("href", "")
        if "Auction results of OFZ" in text and href:
            m = re.search(r"(\d{2})\s([A-Za-z]+),\s(\d{4})", text)
            dt = pd.NaT
            if m:
                try:
                    dt = pd.to_datetime(f"{m.group(1)} {m.group(2)} {m.group(3)}", errors="coerce")
                except Exception:
                    dt = pd.NaT
            rows.append({"date": dt, "title": text, "href": href})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    return df[["date", "title", "href"]].drop_duplicates().reset_index(drop=True)