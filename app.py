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
    st.subheader("Process a Customer Sale (Type Code & Quantity)")

    # Text input for typing Product ID/Code directly
    typed_prod_id = st.text_input("Enter Product ID / Code (e.g., balu 001)")
    qty_sold = st.number_input("Quantity Sold", min_value=1, value=1, step=1, key="sale_qty")

    if st.button("Submit Sale", type="primary"):
        if not typed_prod_id:
            st.error("Please enter a valid Product ID/Code.")
        else:
            # Check if product ID exists in stocks
            matched_row = df_stocks[df_stocks["PRODUCT ID"].astype(str).str.strip().str.lower() == typed_prod_id.strip().lower()]

            if not matched_row.empty:
                product_name = matched_row.iloc[0]["PRODUCT NAME"]

                payload = {
                    "action": "recordSale",
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "time": datetime.now().strftime("%H:%M"),
                    "productId": typed_prod_id.strip(),
                    "productName": product_name,
                    "quantity": int(qty_sold)
                }

                res = requests.post(WEB_APP_URL, json=payload)
                if res.status_code == 200:
                    st.success(f"Sale submitted! Subtracted {qty_sold} from {product_name} ({typed_prod_id}).")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to connect to Google Sheet.")
            else:
                st.error(f"Product ID '{typed_prod_id}' not found in your stocks sheet!")

with tab2:
    st.subheader("Add Incoming Stock (New Purchase)")
    new_prod_id = st.text_input("Product ID / Code", value="balu 033", key="p_id")
    new_prod_name = st.text_input("Product Name", key="p_name")
    qty_purchased = st.number_input("Quantity Purchased", min_value=1, value=1, step=1, key="purchase_qty")

    if st.button("Submit Purchase", type="primary"):
        payload = {
            "action": "recordPurchase",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "time": datetime.now().strftime("%H:%M"),
            "productId": new_prod_id.strip(),
            "productName": new_prod_name.strip(),
            "quantity": int(qty_purchased)
        }

        res = requests.post(WEB_APP_URL, json=payload)
        if res.status_code == 200:
            st.success(f"Successfully added {qty_purchased} units to {new_prod_name}!")
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
