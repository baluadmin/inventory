from datetime import datetime
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Store Inventory Dashboard", page_icon="📦", layout="wide"
)

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwU4S0brHSf2NUXolXiPyCfNtczKmho-Q2K_NHXm8GYTT54pbA7pXhDg8PbBJIh_ejqNQ/exec"

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

tab1, tab2 = st.tabs(["⚡ Record Sale", "📥 Add New Product / Purchase"])

with tab1:
  st.subheader("Process a Customer Sale")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    # Option to search/select by Product ID or Name
    search_mode = st.radio(
        "Search Product By:", ["Product Name", "Product ID"], horizontal=True
    )

    if search_mode == "Product Name":
      product_list = df_stocks["PRODUCT NAME"].dropna().tolist()
      selected_product = st.selectbox(
          "Select Product Name", product_list, key="sale_prod_name"
      )
      matched_row = df_stocks[df_stocks["PRODUCT NAME"] == selected_product]
    else:
      prod_id_list = (
          df_stocks["PRODUCT ID"].dropna().astype(str).tolist()
          if "PRODUCT ID" in df_stocks.columns
          else []
      )
      selected_prod_id = st.selectbox(
          "Select Product ID / Code", prod_id_list, key="sale_prod_id"
      )
      matched_row = df_stocks[
          df_stocks["PRODUCT ID"].astype(str) == str(selected_prod_id)
      ]
      selected_product = (
          matched_row["PRODUCT NAME"].values[0]
          if not matched_row.empty
          else ""
      )

    if not matched_row.empty:
      current_stock_val = matched_row["PRODUCT ID"].values[
          0
      ]  # reference check
      st.info(
          f"Selected: **{selected_product}** (Available Stock:"
          f" {matched_row['STOCK'].values[0] if 'STOCK' in matched_row.columns else 'N/A'})"
      )

    qty_sold = st.number_input(
        "Quantity Sold", min_value=1, value=1, step=1, key="sale_qty"
    )
    not_available = st.text_input("Customer Wanted (Not Available Product)")

    if st.button("Confirm Sale", type="primary"):
      if selected_product:
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
          st.success(
              f"Sale recorded and stock reduced for {selected_product} successfully!"
          )
          st.cache_data.clear()
          st.rerun()
        else:
          err_msg = res_json.get("message", "Unknown error")
          st.error(f"Failed to update Google Sheet: {err_msg}")
      else:
        st.error("Please select a valid product.")
  else:
    st.warning("No products found in stock table.")

with tab2:
  st.subheader("Add New Product or Restock Purchase")
  new_prod_id = st.text_input("Product ID / Code (e.g., 101)")
  new_prod_name = st.text_input("Product Name")
  qty_purchased = st.number_input(
      "Quantity Purchased", min_value=1, value=1, step=1, key="p_qty"
  )
  price = st.number_input(
      "Price", min_value=0.0, value=0.0, step=1.0, key="p_price"
  )

  if st.button("Submit Purchase / Add Stock", type="primary"):
    if new_prod_name.strip():
      payload = {
          "action": "recordPurchase",
          "date": datetime.now().strftime("%Y-%m-%d"),
          "time": datetime.now().strftime("%H:%M:%S"),
          "productId": new_prod_id.strip(),
          "productName": new_prod_name.strip(),
          "qtyPurchased": int(qty_purchased),
          "price": float(price),
      }

      res = requests.post(WEB_APP_URL, json=payload)
      res_json = res.json() if res.status_code == 200 else {}

      if res.status_code == 200 and res_json.get("status") == "success":
        st.success(
            f"Successfully added/updated purchase for {new_prod_name}!"
        )
        st.cache_data.clear()
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update Google Sheet: {err_msg}")
    else:
      st.error("Please enter a valid Product Name.")

st.markdown("---")
st.subheader("📊 Live Stocks Inventory")
if not df_stocks.empty:
  st.dataframe(df_stocks, use_container_width=True)
else:
  st.info("Loading stock data from Google Sheet...")
