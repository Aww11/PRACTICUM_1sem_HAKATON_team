import pandas as pd

def compute_m4(tax: pd.DataFrame) -> pd.DataFrame:
    tax = tax.copy()

    if "date" not in tax.columns:
        tax["date"] = pd.NaT
        if tax.shape[0] > 0:
            tax["date"] = pd.date_range("2024-01-01", periods=len(tax), freq="7D")

    tax["date"] = pd.to_datetime(tax["date"], errors="coerce").dt.normalize()
    tax = tax.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")

    for c in ["tax_week_flag", "end_of_month_flag", "end_of_quarter_flag"]:
        if c not in tax.columns:
            tax[c] = 0

    if "seasonal_factor" not in tax.columns:
        tax["seasonal_factor"] = 1.0

    return tax[["date", "tax_week_flag", "end_of_month_flag", "end_of_quarter_flag", "seasonal_factor"]]