import pandas as pd

def compute_m3(ofz: pd.DataFrame) -> pd.DataFrame:
    ofz = ofz.copy()

    date_col = None
    for c in ofz.columns:
        if "Дата аукциона" in str(c):
            date_col = c
            break

    if date_col is None:
        raise KeyError("ofz: no auction date column found")

    ofz["date"] = pd.to_datetime(ofz[date_col], errors="coerce").dt.normalize()
    ofz = ofz.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")

    cr_col = None
    for c in ofz.columns:
        if "Коэффициент удовлетворения спроса на аукционе" in str(c):
            cr_col = c
            break

    if cr_col is None:
        ofz["cover_ratio_m3"] = pd.NA
    else:
        ofz["cover_ratio_m3"] = pd.to_numeric(ofz[cr_col], errors="coerce")

    ofz["mad_cover_m3"] = ofz["cover_ratio_m3"].rolling(3, min_periods=1).median()
    ofz["flag_nedospros"] = (ofz["cover_ratio_m3"] < 1.2).astype(int)
    ofz["flag_perespros"] = (ofz["cover_ratio_m3"] > 2.0).astype(int)

    return ofz[["date", "cover_ratio_m3", "mad_cover_m3", "flag_nedospros", "flag_perespros"]]