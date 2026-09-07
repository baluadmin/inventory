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
        selected_product = st.selectbox("Select Product", product_list, key="sale_prod")
        qty_sold = st.number_input("Quantity Sold", min_value=1, value=1, step=1, key="sale_qty")

        # Match the columns of your 'sale' tab: Date(A), Time(B), Product ID(C), Product Name(D), Quantity(E)
        selected_row = df_stocks[df_stocks["PRODUCT NAME"] == selected_product].iloc[0]
        prod_id = selected_row.get("PRODUCT ID", "")

        if st.button("Confirm Sale", type="primary"):
            payload = {
                "action": "recordSale",
                "date": datetime.now().strftime("%d/%m/%Y"),
                "time": datetime.now().strftime("%H:%M"),
                "productId": prod_id,
                "productName": selected_product,
                "quantity": int(qty_sold)
            }

            res = requests.post(WEB_APP_URL, json=payload)
            if res.status_code == 200:
                st.success(f"Sale recorded! Subtracted {qty_sold} from {selected_product}.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to connect to Google Sheet.")
    else:
        st.warning("No products found in stock table.")

with tab2:
    st.subheader("Add Incoming Stock (New Purchase)")
    new_prod_id = st.text_input("Product ID", value="balu 033")
    new_prod_name = st.text_input("Product Name")
    qty_purchased = st.number_input("Quantity Purchased", min_value=1, value=1, step=1, key="purchase_qty")

    if st.button("Add Stock", type="primary"):
        payload = {
            "action": "recordPurchase",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "time": datetime.now().strftime("%H:%M"),
            "productId": new_prod_id,
            "productName": new_prod_name,
            "quantity": int(qty_purchased)
        }

        res = requests.post(WEB_APP_URL, json=payload)
        if res.status_code == 200:
            st.success(f"Successfully added {qty_purchased} units of {new_prod_name}!")
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
