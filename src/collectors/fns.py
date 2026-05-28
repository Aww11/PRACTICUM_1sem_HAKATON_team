import pandas as pd
from src.collectors._helpers import safe_read_html

FNS_CALENDAR_URL = "https://www.nalog.gov.ru/rn77/calendar/"

def fetch_tax_calendar() -> pd.DataFrame:
    tables = safe_read_html(FNS_CALENDAR_URL)
    if not tables:
        return pd.DataFrame()
    df = tables[0].copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df