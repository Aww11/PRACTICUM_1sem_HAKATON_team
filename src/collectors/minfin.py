import pandas as pd
from src.collectors._helpers import safe_read_html

MINFIN_URL = "https://minfin.gov.ru/ru/document?id_4=315131-rezultaty_provedennykh_auktsionov_po_razmeshcheniyu_gosudarstvennykh_tsennykh_bumag_v_2026_godu_na_26.02.2026"

def fetch_ofz_auctions() -> pd.DataFrame:
    tables = safe_read_html(MINFIN_URL)
    if not tables:
        return pd.DataFrame()
    df = tables[0].copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df