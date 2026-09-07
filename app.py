from datetime import datetime
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Store Inventory Dashboard", page_icon="📦", layout="wide"
)

WEB_APP_URL = "YOUR_NEW_DEPLOYED_WEB_APP_URL_HERE"

st.title("📦 Store Inventory & Sales Management System")
st.markdown("---")


@st.cache_data(ttl=0)
def get_stocks():
  try:
    response = requests.get(WEB_APP_URL)
    return response.json()
  except Exception:
    return []


stocks_data = get_stocks()
df_stocks = pd.DataFrame(stocks_data)

tab1, tab2 = st.tabs(["⚡ Record Sale", "📥 Add New Purchase"])

with tab1:
  st.subheader("Process a Customer Sale")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    product_list = df_stocks["PRODUCT NAME"].tolist()
    selected_product = st.selectbox(
        "Select Product", product_list, key="sale_prod"
    )
    qty_sold = st.number_input(
        "Quantity Sold", min_value=1, value=1, step=1, key="sale_qty"
    )
    not_available = st.text_input("Customer Wanted (Not Available Product)")

    if st.button("Confirm Sale", type="primary"):
      payload = {
          "action": "recordSale",
          "date": datetime.now().strftime("%Y-%m-%d"),
          "time": datetime.now().strftime("%H:%M:%S"),
          "productName": selected_product,
          "qtySold": int(qty_sold),
          "notAvailable": not_available,
      }

      res = requests.post(WEB_APP_URL, json=payload)
      res_json = res.json() if res.status_code == 200 else {}

      if res.status_code == 200 and res_json.get("status") == "success":
        st.success(f"Sale recorded successfully for {selected_product}!")
        st.cache_data.clear()
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update Google Sheet: {err_msg}")
  else:
    st.warning("No products found in stock table.")

with tab2:
  st.subheader("Add Incoming Stock (New Purchase)")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    product_list_p = df_stocks["PRODUCT NAME"].tolist()
    selected_product_p = st.selectbox(
        "Select Product", product_list_p, key="purchase_prod"
    )
    qty_purchased = st.number_input(
        "Quantity Purchased", min_value=1, value=1, step=1, key="purchase_qty"
    )

    if st.button("Add Stock", type="primary"):
      payload = {
          "action": "recordPurchase",
          "date": datetime.now().strftime("%Y-%m-%d"),
          "time": datetime.now().strftime("%H:%M:%S"),
          "productName": selected_product_p,
          "qtyPurchased": int(qty_purchased),
      }

      res = requests.post(WEB_APP_URL, json=payload)
      res_json = res.json() if res.status_code == 200 else {}

      if res.status_code == 200 and res_json.get("status") == "success":
        st.success(
            f"Successfully added {qty_purchased} units to {selected_product_p}!"
        )
        st.cache_data.clear()
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update Google Sheet: {err_msg}")

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
  st.dataframe(df_stocks, use_container_width=True)
else:
  st.info("Loading stock data from Google Sheet...")
