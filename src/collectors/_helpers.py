import pandas as pd
import requests
from io import StringIO
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        return r.text
    except SSLError:
        r = requests.get(url, headers=headers, timeout=60, verify=False)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""

def safe_read_html(url: str) -> list[pd.DataFrame]:
    html = fetch_html(url)
    if not html:
        return []
    for flavor in ("lxml", "html5lib"):
        try:
            tables = pd.read_html(StringIO(html), flavor=flavor)
            if tables:
                return tables
        except Exception:
            pass
    try:
        return pd.read_html(StringIO(html))
    except Exception:
        return []

def first_table(url: str) -> pd.DataFrame:
    tables = safe_read_html(url)
    if not tables:
        return pd.DataFrame()
    df = tables[0].copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def pick_table_by_keywords(tables: list[pd.DataFrame], keywords: list[str]) -> pd.DataFrame:
    if not tables:
        return pd.DataFrame()
    kws = [k.lower() for k in keywords]
    for t in tables:
        cols = " | ".join(map(str, t.columns)).lower()
        if all(k in cols for k in kws):
            df = t.copy()
            df.columns = [str(c).strip() for c in df.columns]
            return df
    df = tables[0].copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df