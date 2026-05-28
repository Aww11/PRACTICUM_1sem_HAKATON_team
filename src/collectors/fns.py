import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def fetch_tax_calendar():
    urls = [
        "https://www.nalog.gov.ru/eng/",
        "https://www.nalog.gov.ru/rn77/news/",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    rows = []

    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        dates = re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", text)
        for d in dates[:10]:
            rows.append({"date": pd.to_datetime(d, dayfirst=True, errors="coerce"), "tax_event": 1})

        if rows:
            break

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    return df