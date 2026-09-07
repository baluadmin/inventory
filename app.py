import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Store Billing & Inventory System", page_icon="🧾", layout="wide")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwU4S0brHSf2NUXolXiPyCfNtczKmho-Q2K_NHXm8GYTT54pbA7pXhDg8PbBJIh_ejqNQ/exec"

st.title("🧾 Store Billing & Sales Management System")
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

if "bill_cart" not in st.session_state:
    st.session_state.bill_cart = []

tab1, tab2 = st.tabs(["🧾 Billing Counter", "📥 Add New Purchase"])

with tab1:
    st.subheader("Point of Sale (POS) Billing Counter")

    if not df_stocks.empty and "PRODUCT ID" in df_stocks.columns:
        # Ensure price column exists or default to a standard price if not in sheet
        if "PRICE" not in df_stocks.columns:
            df_stocks["PRICE"] = 100.0  # Default item price placeholder if not in Google Sheet

        df_stocks["display"] = df_stocks["PRODUCT ID"].astype(str) + " - " + df_stocks["PRODUCT NAME"].astype(str) + " (Stock: " + df_stocks["STOCK"].astype(str) + ")"

        col_a, col_b = st.columns([2, 1])
        with col_a:
            selected_item = st.selectbox("Select Product to Bill", df_stocks["display"].tolist())
        with col_b:
            qty_to_buy = st.number_input("Quantity", min_value=1, value=1, step=1)

        if st.button("Add to Bill Item List", type="primary"):
            matched_row = df_stocks[df_stocks["display"] == selected_item].iloc[0]
            p_id = str(matched_row["PRODUCT ID"])
            p_name = str(matched_row["PRODUCT NAME"])
            p_price = float(matched_row.get("PRICE", 100.0))
            current_stock = int(matched_row["STOCK"])

            if qty_to_buy > current_stock:
                st.error(f"Only {current_stock} units available in stock!")
            else:
                # Add or update item in billing cart
                existing = next((item for item in st.session_state.bill_cart if item["productId"] == p_id), None)
                if existing:
                    existing["quantity"] += int(qty_to_buy)
                    existing["totalPrice"] = existing["quantity"] * existing["unitPrice"]
                else:
                    st.session_state.bill_cart.append({
                        "productId": p_id,
                        "productName": p_name,
                        "unitPrice": p_price,
                        "quantity": int(qty_to_buy),
                        "totalPrice": p_price * int(qty_to_buy)
                    })
                st.success(f"Added {qty_to_buy}x {p_name} to bill.")

        # Display Invoice Table & Grand Total
        if st.session_state.bill_cart:
            st.markdown("### 📋 Current Bill Invoice")
            df_bill = pd.DataFrame(st.session_state.bill_cart)
            st.dataframe(df_bill, use_container_width=True)

            grand_total = df_bill["totalPrice"].sum()
            st.markdown(f"## 💰 Grand Total: ₹ {grand_total:,.2f}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Complete Checkout & Deduct Stock", type="primary"):
                    current_time = datetime.now().strftime("%H:%M")
                    current_date = datetime.now().strftime("%d/%m/%Y")
                    success_all = True

                    for item in st.session_state.bill_cart:
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
                        st.success("Billing complete! Google Sheet stocks updated successfully.")
                        st.session_state.bill_cart = []
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Billing submission failed.")
            with col2:
                if st.button("🗑️ Clear Bill"):
                    st.session_state.bill_cart = []
                    st.rerun()
    else:
        st.warning("Loading inventory items...")

with tab2:
    st.subheader("Add Incoming Stock (New Purchase)")
    with st.form("purchase_form"):
        p_id = st.text_input("Product ID / Code")
        p_name = st.text_input("Product Name")
        p_qty = st.number_input("Quantity Purchased", min_value=1, value=1, step=1)

        submitted = st.form_submit_button("Submit Purchase", type="primary")
        if submitted and p_id and p_name:
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
                st.success(f"Successfully added {p_qty} units of {p_name}!")
                st.cache_data.clear()
                st.rerun()

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
    st.dataframe(df_stocks.drop(columns=["display"], errors="ignore"), use_container_width=True)
