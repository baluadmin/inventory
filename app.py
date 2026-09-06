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
        return response.json()
    except:
        return []

stocks_data = get_stocks()
df_stocks = pd.DataFrame(stocks_data)

tab1, tab2 = st.tabs(["⚡ Record Sale", "📥 Add New Purchase"])

with tab1:
    st.subheader("Process a Customer Sale")
    if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
        product_list = df_stocks["PRODUCT NAME"].tolist()
        selected_product = st.selectbox("Select Product (Sale)", product_list, key="sale_prod")
        qty_sold = st.number_input("Quantity Sold", min_value=1, value=1, step=1, key="sale_qty")
        not_available = st.text_input("Customer Wanted (Not Available Product)")

        if st.button("Confirm Sale", type="primary"):
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
                st.success(f"Sale recorded! Stock updated for {selected_product}: {stock_after_sale}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to connect to Google Sheet.")
    else:
        st.warning("No products found in stock table.")

with tab2:
    st.subheader("Add Incoming Stock (New Purchase)")
    if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
        product_list_p = df_stocks["PRODUCT NAME"].tolist()
        selected_product_p = st.selectbox("Select Product (Purchase)", product_list_p, key="purchase_prod")
        qty_purchased = st.number_input("Quantity Purchased / Added", min_value=1, value=1, step=1, key="purchase_qty")

        if st.button("Add Stock", type="primary"):
            payload = {
                "action": "recordPurchase",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "productName": selected_product_p,
                "qtyPurchased": int(qty_purchased)
            }

            res = requests.post(WEB_APP_URL, json=payload)
            if res.status_code == 200:
                st.success(f"Successfully added {qty_purchased} units to {selected_product_p}!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to connect to Google Sheet.")

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
    st.dataframe(df_stocks, use_container_width=True)
else:
    st.info("Loading stock data from Google Sheet...")
