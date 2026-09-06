import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Store Inventory Dashboard", page_icon="📦", layout="wide")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwU4S0brHSf2NUXolXiPyCfNtczKmho-Q2K_NHXm8GYTT54pbA7pXhDg8PbBJIh_ejqNQ/exec"

st.title("📦 Store Inventory & Sales Management System")
st.markdown("---")

@st.cache_data(ttl=2)
def get_stocks():
    try:
        response = requests.get(WEB_APP_URL)
        # Check if response is valid JSON
        return response.json()
    except Exception as e:
        return None

stocks_data = get_stocks()

if stocks_data is None or not isinstance(stocks_data, list):
    st.error("⚠️ Could not load data from Google Sheets. Please ensure your Apps Script is deployed with 'Who has access' set to **'Anyone'**.")
    st.stop()

df_stocks = pd.DataFrame(stocks_data)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("⚡ Record Daily Sale")
    if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
        product_list = df_stocks["PRODUCT NAME"].tolist()
        selected_product = st.selectbox("Select Product", product_list)
        qty_sold = st.number_input("Quantity Sold", min_value=1, value=1, step=1)
        not_available = st.text_input("Customer Wanted (Not Available Product)")

        if st.button("Record Sale", type="primary"):
            current_row = df_stocks[df_stocks["PRODUCT NAME"] == selected_product].iloc[0]
            current_stock = int(current_row["STOCK"])
            stock_after_sale = current_stock - int(qty_sold)

            payload = {
                "action": "recordSale",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "productName": selected_product,
                "stockAfterSale": stock_after_sale,
                "notAvailable": not_available
            }

            res = requests.post(WEB_APP_URL, json=payload)
            if res.status_code == 200:
                st.success(f"Sale recorded successfully! Updated stock for {selected_product}: {stock_after_sale}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to connect to Google Sheet backend.")
    else:
        st.warning("No product data found. Check your 'stocks' tab column headers (`PRODUCT ID`, `PRODUCT NAME`, `STOCK`).")

with col2:
    st.subheader("📊 Live Stocks Inventory")
    if not df_stocks.empty:
        st.dataframe(df_stocks, use_container_width=True)
    else:
        st.info("Loading stock data from Google Sheet...")
