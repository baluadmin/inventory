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

tab1, tab2 = st.tabs(["⚡ Quick Sale", "📥 Add New Purchase"])

with tab1:
    st.subheader("Quick Multi-Product Sale")

    if not df_stocks.empty and "PRODUCT ID" in df_stocks.columns:
        # Create a simple form for quick entries
        with st.form("quick_sale_form"):
            col1, col2 = st.columns(2)
            with col1:
                prod1_id = st.text_input("Product ID 1 (e.g., 1)")
                qty1 = st.number_input("Quantity 1", min_value=0, value=0, step=1)

                prod2_id = st.text_input("Product ID 2 (e.g., 2)")
                qty2 = st.number_input("Quantity 2", min_value=0, value=0, step=1)

            with col2:
                prod3_id = st.text_input("Product ID 3")
                qty3 = st.number_input("Quantity 3", min_value=0, value=0, step=1)

                prod4_id = st.text_input("Product ID 4")
                qty4 = st.number_input("Quantity 4", min_value=0, value=0, step=1)

            submit_btn = st.form_submit_button("🚀 Submit All Sales", type="primary")

            if submit_btn:
                entries = [
                    (prod1_id.strip(), qty1),
                    (prod2_id.strip(), qty2),
                    (prod3_id.strip(), qty3),
                    (prod4_id.strip(), qty4)
                ]

                current_time = datetime.now().strftime("%H:%M")
                current_date = datetime.now().strftime("%d/%m/%Y")
                success_count = 0

                for p_id, q in entries:
                    if p_id and q > 0:
                        matched_row = df_stocks[df_stocks["PRODUCT ID"].astype(str).str.strip().str.lower() == p_id.lower()]
                        if not matched_row.empty:
                            prod_name = matched_row.iloc[0]["PRODUCT NAME"]
                            current_stock = int(matched_row.iloc[0]["STOCK"])

                            if q <= current_stock:
                                payload = {
                                    "action": "recordSale",
                                    "date": current_date,
                                    "time": current_time,
                                    "productId": p_id,
                                    "productName": prod_name,
                                    "quantity": int(q)
                                }
                                res = requests.post(WEB_APP_URL, json=payload)
                                if res.status_code == 200:
                                    success_count += 1
                            else:
                                st.error(f"Not enough stock for Product ID {p_id}!")

                if success_count > 0:
                    st.success(f"Successfully submitted {success_count} sale(s) and updated Google Sheet!")
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.warning("Loading stock data...")

with tab2:
    st.subheader("Add New Purchase")
    with st.form("purchase_form"):
        p_id = st.text_input("Product ID / Code")
        p_name = st.text_input("Product Name")
        p_qty = st.number_input("Quantity Purchased", min_value=1, value=1, step=1)

        p_submit = st.form_submit_button("Submit Purchase", type="primary")
        if p_submit and p_id and p_name:
            payload = {
                "action": "recordPurchase",
                "date": datetime.now().strftime("%d/%m/%Y"),
                "time": datetime.now().strftime("%H:%M"),
                "productId": p_id.strip(),
                "productName": p_name.strip(),
                "quantity": int(p_qty)
            }
            res = requests.post(WEB_APP_URL, json=payload)
            if res.status_code == 200:
                st.success(f"Added {p_qty} units of {p_name}!")
                st.cache_data.clear()
                st.rerun()

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
    st.dataframe(df_stocks, use_container_width=True)
