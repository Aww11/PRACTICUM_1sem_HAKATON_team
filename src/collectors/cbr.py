import pandas as pd
from src.collectors._helpers import safe_read_html, first_table, pick_table_by_keywords

CBR_RRESERVES_URL = "https://www.cbr.ru/eng/hd_base/RReserves/"
CBR_RUONIA_URL = "https://www.cbr.ru/eng/hd_base/ruonia/"
CBR_RUONIA_AVG_URL = "https://www.cbr.ru/eng/hd_base/ruonia/sv_ruonia/"
CBR_REPO_URL = "https://www.cbr.ru/eng/hd_base/repo/"
CBR_KEYRATE_URL = "https://www.cbr.ru/eng/hd_base/KeyRate/"
CBR_BLIQUIDITY_URL = "https://www.cbr.ru/eng/hd_base/bliquidity/"

def fetch_required_reserves() -> pd.DataFrame:
    tables = safe_read_html(CBR_RRESERVES_URL)
    return pick_table_by_keywords(tables, ["required reserves"]) if tables else pd.DataFrame()

def fetch_ruonia() -> pd.DataFrame:
    tables = safe_read_html(CBR_RUONIA_URL)
    return pick_table_by_keywords(tables, ["ruonia"]) if tables else pd.DataFrame()

def fetch_ruonia_avg() -> pd.DataFrame:
    tables = safe_read_html(CBR_RUONIA_AVG_URL)
    return pick_table_by_keywords(tables, ["index"]) if tables else pd.DataFrame()

def fetch_repo_auctions() -> pd.DataFrame:
    tables = safe_read_html(CBR_REPO_URL)
    return pick_table_by_keywords(tables, ["repo"]) if tables else pd.DataFrame()

def fetch_key_rate() -> pd.DataFrame:
    tables = safe_read_html(CBR_KEYRATE_URL)
    return pick_table_by_keywords(tables, ["key rate"]) if tables else pd.DataFrame()

def fetch_bliquidity() -> pd.DataFrame:
    tables = safe_read_html(CBR_BLIQUIDITY_URL)
    return pick_table_by_keywords(tables, ["liquidity"]) if tables else pd.DataFrame()