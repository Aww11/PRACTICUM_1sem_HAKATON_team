import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="RU Liquidity Sentinel", layout="wide")
st.title("RU Liquidity Sentinel")


@st.cache_data
def load_data():
    df = pd.read_csv("output/lsi_output.csv", parse_dates=["date"])
    df = df.sort_values("date").dropna(subset=["date"])
    return df


try:
    df = load_data()
except Exception:
    st.warning("Сначала запустите pipeline.py")
    st.stop()

if df.empty:
    st.warning("Данные пустые.")
    st.stop()

min_dt = df["date"].min().date()
max_dt = df["date"].max().date()
default_start = df["date"].iloc[max(0, len(df) - 90)].date() if len(df) > 90 else min_dt
default_end = max_dt

date_range = st.date_input(
    "Выберите диапазон дат",
    value=(default_start, default_end),
    min_value=min_dt,
    max_value=max_dt,
)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.error("Нужно выбрать диапазон из двух дат.")
    st.stop()

start_date, end_date = date_range
view = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()

if view.empty:
    st.warning("За выбранный период нет данных.")
    st.stop()

last = view.iloc[-1]
lsi_val = last["lsi"] if "lsi" in last else pd.NA
status_val = last["status"] if "status" in last else "Neutral / Insufficient data"
quality_val = last["data_quality"] if "data_quality" in last else "UNKNOWN"

if pd.isna(lsi_val) or quality_val != "OK":
    status_display = "Neutral / Insufficient data"
    lsi_display = "—"
else:
    status_display = str(status_val)
    lsi_display = f"{float(lsi_val):.1f}"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Текущий LSI", lsi_display)
c2.metric("Статус", status_display)
c3.metric("Последняя дата", str(last["date"].date()))
c4.metric("Строк в диапазоне", len(view))

c5, c6, c7 = st.columns(3)
c5.metric("Средний LSI", "—" if view["lsi"].dropna().empty else f"{view['lsi'].mean():.1f}")
c6.metric("Максимальный LSI", "—" if view["lsi"].dropna().empty else f"{view['lsi'].max():.1f}")
nonzero = view[view["lsi"].fillna(0) != 0]
c7.metric("Последний ненулевой LSI", "—" if nonzero.empty else f"{nonzero['lsi'].iloc[-1]:.1f}")

fig = px.line(view, x="date", y="lsi", title="Liquidity Stress Index")
st.plotly_chart(fig, width="stretch")

default_cols = [c for c in ["date", "lsi", "status", "data_quality", "m1", "m2", "m3", "m4", "m5"] if c in view.columns]
all_cols = list(view.columns)

selected_cols = st.multiselect(
    "Показать столбцы",
    options=all_cols,
    default=default_cols,
)

show_df = view[selected_cols].tail(20).copy() if selected_cols else view.tail(20).copy()
if "date" in show_df.columns:
    show_df["date"] = pd.to_datetime(show_df["date"]).dt.strftime("%Y-%m-%d")

st.subheader("Данные за выбранный период")
st.dataframe(
    show_df,
    width="stretch",
    hide_index=True,
)