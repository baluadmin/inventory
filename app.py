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

if "cart" not in st.session_state:
    st.session_state.cart = []

tab1, tab2 = st.tabs(["⚡ Record Sale", "📥 Add New Purchase"])

with tab1:
    st.subheader("Process Customer Sale (Select & Add)")

    if not df_stocks.empty and "PRODUCT ID" in df_stocks.columns:
        # Create a friendly dropdown choice combining ID and Product Name
        df_stocks["display_name"] = df_stocks["PRODUCT ID"].astype(str) + " - " + df_stocks["PRODUCT NAME"].astype(str)
        selected_display = st.selectbox("Select Product", df_stocks["display_name"].tolist())

        qty_sold = st.number_input("Quantity Sold", min_value=1, value=1, step=1, key="easy_qty")

        if st.button("➕ Add to Cart", type="primary"):
            selected_row = df_stocks[df_stocks["display_name"] == selected_display].iloc[0]
            prod_id = str(selected_row["PRODUCT ID"])
            prod_name = str(selected_row["PRODUCT NAME"])
            current_stock = int(selected_row["STOCK"])

            if qty_sold > current_stock:
                st.error(f"Only {current_stock} left in stock for {prod_name}!")
            else:
                # Check if already in cart, update quantity if it is
                existing_item = next((item for item in st.session_state.cart if item["productId"] == prod_id), None)
                if existing_item:
                    existing_item["quantity"] += int(qty_sold)
                else:
                    st.session_state.cart.append({
                        "productId": prod_id,
                        "productName": prod_name,
                        "quantity": int(qty_sold)
                    })
                st.success(f"Added {qty_sold}x {prod_name} to cart.")
    else:
        st.warning("Loading products or no stock found...")

    # Show Cart
    if st.session_state.cart:
        st.markdown("### 🛒 Cart Summary")
        st.dataframe(pd.DataFrame(st.session_state.cart), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Checkout All Items", type="primary"):
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
                    st.success("Checkout successful! Stocks updated in Google Sheets.")
                    st.session_state.cart = []
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Checkout failed. Check connection.")
        with col2:
            if st.button("🗑️ Clear Cart"):
                st.session_state.cart = []
                st.rerun()

with tab2:
    st.subheader("Add Incoming Stock (New Purchase)")
    new_prod_id = st.text_input("Product ID / Code", value="3")
    new_prod_name = st.text_input("Product Name")
    qty_purchased = st.number_input("Quantity Purchased", min_value=1, value=1, step=1, key="p_qty")

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
            st.error("Failed to connect.")

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
    st.dataframe(df_stocks.drop(columns=["display_name"], errors="ignore"), use_container_width=True)
