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

# Initialize shopping cart in session state
if "cart" not in st.session_state:
    st.session_state.cart = []

tab1, tab2 = st.tabs(["⚡ Record Sale (Multi-Item Cart)", "📥 Add New Purchase"])

with tab1:
    st.subheader("Process Customer Sale with Multiple Products")

    typed_prod_id = st.text_input("Enter Product ID / Code")
    qty_sold = st.number_input("Quantity", min_value=1, value=1, step=1, key="cart_qty")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add to Cart"):
            if not typed_prod_id:
                st.error("Please enter a Product ID.")
            else:
                matched_row = df_stocks[df_stocks["PRODUCT ID"].astype(str).str.strip().str.lower() == typed_prod_id.strip().lower()]
                if not matched_row.empty:
                    prod_name = matched_row.iloc[0]["PRODUCT NAME"]
                    current_stock = int(matched_row.iloc[0]["STOCK"])

                    if qty_sold > current_stock:
                        st.error(f"Only {current_stock} left in stock for {prod_name}!")
                    else:
                        st.session_state.cart.append({
                            "productId": typed_prod_id.strip(),
                            "productName": prod_name,
                            "quantity": int(qty_sold)
                        })
                        st.success(f"Added {qty_sold}x {prod_name} to cart.")
                else:
                    st.error("Product ID not found!")

    # Display current cart items
    if st.session_state.cart:
        st.markdown("### 🛒 Current Cart Items")
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(df_cart, use_container_width=True)

        if st.button("Checkout & Submit All Sales", type="primary"):
            success_all = True
            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%d/%m/%Y")

            for item in st.session_state.cart:
                payload = {
                    "action": "recordSale",
                    "date": current_date,
                    "time": current_time,
                    "productId": item["productId"],
                    "productName": item["productName"],
                    "quantity": item["quantity"]
                }
                res = requests.post(WEB_APP_URL, json=payload)
                if res.status_code != 200:
                    success_all = False

            if success_all:
                st.success("All items checked out successfully and stocks updated!")
                st.session_state.cart = []
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Error communicating with Google Sheet during checkout.")

        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.rerun()

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
