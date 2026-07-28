import streamlit as st
import requests
import csv
import os
import pandas as pd
from datetime import datetime

HISTORY_FILE = "fx_history.csv"

def fetch_rate(base, target):
    url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(url)
    data = response.json()
    return data["rates"][target]

def log_rate(rate):
    file_exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "rate"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rate])

def load_history():
    return pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])

def calc_daily_change(history_df, current_rate):
    if len(history_df) < 2:
        return 0.0
    cutoff = datetime.now() - pd.Timedelta(hours=24)
    past_rows = history_df[history_df["timestamp"] <= cutoff]
    if past_rows.empty:
        old_rate = history_df.iloc[0]["rate"]
    else:
        old_rate = past_rows.iloc[-1]["rate"]
    return ((current_rate - old_rate) / old_rate) * 100

st.title("GBP/AED Exchange Rate Tracker")

BASE_CURRENCY = "GBP"
TARGET_CURRENCY = "AED"

current_rate = fetch_rate(BASE_CURRENCY, TARGET_CURRENCY)
log_rate(current_rate)
history = load_history()
daily_change = calc_daily_change(history, current_rate)

st.metric(
    label=f"{BASE_CURRENCY}/{TARGET_CURRENCY}",
    value=f"{current_rate:.4f}",
    delta=f"{daily_change:.2f}%"
)

st.subheader("Historical Rate Trend")
chart_data = history.set_index("timestamp")["rate"]
st.line_chart(chart_data)

st.subheader("Rate Alert")
threshold = st.number_input("Alert me when rate crosses:", value=0.0, step=0.01)

if threshold > 0:
    if current_rate >= threshold:
        st.warning(f"⚠️ {BASE_CURRENCY}/{TARGET_CURRENCY} has crossed your threshold of {threshold:.4f} — currently at {current_rate:.4f}")
    else:
        st.info(f"Current rate {current_rate:.4f} is below your threshold of {threshold:.4f}")

st.subheader("Market Commentary")
st.markdown("""
*[Partner's written commentary goes here — replace this placeholder text   
once they've written it up.]*
""")

if st.button("Refresh Now"):
    st.rerun()
