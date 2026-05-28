import pandas as pd
from src.collectors._helpers import safe_read_html

ROSKAZNA_URL = "https://roskazna.gov.ru/finansovye-operacii/razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta/razmeshchenie-sredstv-edinogo-kaznachejskogo-scheta-na-bankovskih-depozitah"

def fetch_treasury_deposits() -> pd.DataFrame:
    tables = safe_read_html(ROSKAZNA_URL)
    if not tables:
        return pd.DataFrame()
    df = tables[0].copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df