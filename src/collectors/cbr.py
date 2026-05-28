import pandas as pd
import requests
from io import StringIO


def _read_tables(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return pd.read_html(StringIO(resp.text))


def fetch_required_reserves():
    url = "https://www.cbr.ru/eng/oper_br/o_dkp/reserve_requirements/"
    try:
        tables = _read_tables(url)
    except Exception as e:
        print("reserves read error:", repr(e))
        return pd.DataFrame()

    if not tables:
        print("reserves tables found: 0")
        return pd.DataFrame()

    for t in tables:
        cols = [str(c) for c in t.columns]
        if any("Averaging Period Starting on" in c for c in cols):
            date_col = next(c for c in t.columns if "Averaging Period Starting on" in str(c))
            rr_col = next((c for c in t.columns if "Required Reserves to be Averaged" in str(c)), None)
            if rr_col is None and t.shape[1] >= 3:
                rr_col = t.columns[2]

            out = t[[date_col, rr_col]].copy()
            out.columns = ["date", "required_reserves"]
            out["date"] = pd.to_datetime(out["date"], dayfirst=True, errors="coerce").dt.normalize()
            out["required_reserves"] = pd.to_numeric(out["required_reserves"], errors="coerce")
            out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
            return out

    print("reserves target table not found")
    return pd.DataFrame()


def fetch_ruonia():
    url = "https://www.cbr.ru/eng/hd_base/ruonia/"
    try:
        tables = _read_tables(url)
    except Exception:
        return pd.DataFrame()

    if not tables:
        return pd.DataFrame()

    df = tables[0].copy()
    if df.shape[0] < 2:
        return pd.DataFrame()

    date_row = df.iloc[0]
    value_row = df.iloc[1]

    out = pd.DataFrame({
        "date": pd.to_datetime(date_row[1:], dayfirst=True, errors="coerce"),
        "ruonia": pd.to_numeric(value_row[1:], errors="coerce"),
    })
    out["date"] = out["date"].dt.normalize()
    out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    return out


def fetch_ruonia_avg():
    url = "https://www.cbr.ru/eng/hd_base/ruonia/dynamic/"
    try:
        tables = _read_tables(url)
    except Exception:
        return pd.DataFrame()

    if not tables:
        return pd.DataFrame()

    df = tables[0].copy()
    cols = [str(c).strip() for c in df.columns]

    if len(cols) < 3:
        return pd.DataFrame()

    date_col = df.columns[0]
    avg_col = None
    for c in df.columns:
        if "1 month" in str(c).lower():
            avg_col = c
            break
    if avg_col is None:
        avg_col = df.columns[2]

    out = df[[date_col, avg_col]].copy()
    out.columns = ["date", "ruonia_avg"]
    out["date"] = pd.to_datetime(out["date"], dayfirst=True, errors="coerce").dt.normalize()
    out["ruonia_avg"] = pd.to_numeric(out["ruonia_avg"], errors="coerce")
    out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    return out


def fetch_repo_auctions():
    url = "https://www.cbr.ru/eng/hd_base/repo/"
    try:
        tables = _read_tables(url)
    except Exception:
        return pd.DataFrame()

    if not tables:
        return pd.DataFrame()

    df = tables[0].copy()

    if df.shape[1] == 2:
        out = df.copy()
        out.columns = ["metric", "value"]
        out["date"] = pd.Timestamp.today().normalize()
        return out

    return pd.DataFrame()


def fetch_key_rate():
    url = "https://www.cbr.ru/eng/hd_base/keyrate/"
    try:
        tables = _read_tables(url)
    except Exception:
        return pd.DataFrame()

    if not tables:
        return pd.DataFrame()

    df = tables[0].copy()
    if df.shape[1] < 2:
        return pd.DataFrame()

    date_col = next((c for c in df.columns if "Date" in str(c) or "Дата" in str(c)), df.columns[0])
    rate_col = next((c for c in df.columns if "Rate" in str(c) or "Ставка" in str(c)), df.columns[1])

    out = df[[date_col, rate_col]].copy()
    out.columns = ["date", "key_rate"]
    out["date"] = pd.to_datetime(out["date"], dayfirst=True, errors="coerce").dt.normalize()
    out["key_rate"] = pd.to_numeric(out["key_rate"], errors="coerce")
    out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    return out


def fetch_bliquidity():
    url = "https://www.cbr.ru/eng/hd_base/liquidity/"
    try:
        tables = _read_tables(url)
    except Exception:
        return pd.DataFrame()

    if not tables:
        return pd.DataFrame()
    return tables[0].copy()