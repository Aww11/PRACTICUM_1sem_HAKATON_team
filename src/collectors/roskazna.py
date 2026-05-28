import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def fetch_treasury_deposits():
    urls = [
        "https://roskazna.gov.ru/",
        "https://os.roskazna.gov.ru/news/",
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

        nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
        if nums:
            rows.append({
                "date": pd.Timestamp.today().normalize(),
                "treasury_amount": float(str(nums[0]).replace(",", ".")),
            })
            break

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)