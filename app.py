from datetime import datetime
from zoneinfo import ZoneInfo
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Bavesh Inventory", page_icon="🌿", layout="wide"
)

# Professional CSS to enforce Dark Violet/White theme, full-width table coverage, and centered text
st.markdown(
    """
    <style>
    .stApp {
        background-color: #2b1b3d !important;
        color: #f3f0f7 !important;
    }
    
    .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #f3f0f7 !important;
        font-weight: 600 !important;
    }

    .stButton>button {
        background-color: #7b2cbf !important;
        color: white !important;
        font-weight: 600;
        font-size: 15px;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #9d4edd !important;
        color: white !important;
    }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    h1, h2, h3, h4, h5, h6 {
        color: #f3f0f7 !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }

    table {
        width: 100% !important;
        margin: auto;
        border-collapse: collapse;
        background-color: #3c2a54;
        color: #f3f0f7;
        border-radius: 6px;
        overflow: hidden;
    }
    th {
        background-color: #5a189a !important;
        color: white !important;
        text-align: center !important;
        padding: 12px;
        font-size: 16px;
    }
    td {
        text-align: center !important;
        padding: 10px;
        border-bottom: 1px solid #4a3468;
        font-size: 15px;
        color: #f3f0f7 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwU4S0brHSf2NUXolXiPyCfNtczKmho-Q2K_NHXm8GYTT54pbA7pXhDg8PbBJIh_ejqNQ/exec"

if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
  st.markdown(
      "<h2 style='color: #e0aaff; font-size: 1.8rem;'>Bavesh System Login</h2>",
      unsafe_allow_html=True,
  )
  st.markdown("Please enter your credentials to access the inventory system.")

  with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_btn = st.form_submit_button("Login", type="primary")

    if submit_btn:
      if username == "bavesh" and password == "Balu@123":
        st.session_state["authenticated"] = True
        st.success("Login successful!")
        st.rerun()
      else:
        st.error("Invalid username or password.")
  st.stop()

st.markdown(
    "<h1 style='text-align: center; color: #e0aaff; font-size: 2.2rem;"
    " margin-bottom: 0;'>Bavesh Inventory & Sales Management System</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")


def get_stocks():
  try:
    fresh_url = f"{WEB_APP_URL}?t={time.time()}"
    response = requests.get(fresh_url)
    return response.json()
  except Exception:
    return []


stocks_data = get_stocks()
df_stocks = pd.DataFrame(stocks_data)

tab1, tab2 = st.tabs(["Record Multi-Item Sale", "Add New Product / Purchase"])

with tab1:
  st.subheader("Process a Multi-Item Customer Sale")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    # Create formatted labels displaying Product Name alongside its current stock level
    df_stocks["DISPLAY_LABEL"] = (
        df_stocks["PRODUCT NAME"]
        + " (Stock: "
        + df_stocks["STOCK"].astype(str)
        + ")"
    )
    product_options = df_stocks["DISPLAY_LABEL"].tolist()
    product_name_mapping = dict(
        zip(df_stocks["DISPLAY_LABEL"], df_stocks["PRODUCT NAME"])
    )

    if "cart" not in st.session_state:
      st.session_state["cart"] = []

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
      selected_display = st.selectbox(
          "Select Product (with live stock)",
          options=product_options,
          key="cart_product",
      )
      selected_product = product_name_mapping[selected_display]
    with col2:
      qty_sold = st.number_input(
          "Quantity", min_value=1, value=1, step=1, key="cart_qty"
      )
    with col3:
      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("Add to Bill"):
        matched_row = df_stocks[df_stocks["PRODUCT NAME"] == selected_product]

        if not matched_row.empty:
          available_stock = (
              int(matched_row["STOCK"].values[0])
              if "STOCK" in matched_row.columns
              else 0
          )
          unit_price = (
              float(matched_row["PRICE"].values[0])
              if "PRICE" in matched_row.columns
              else 0.0
          )

          if qty_sold > available_stock:
            st.warning(
                f"⚠️ Warning: Requested quantity ({qty_sold}) exceeds available"
                f" stock ({available_stock}) for {selected_product}!"
            )

          total_price = qty_sold * unit_price

          existing_item = next(
              (
                  item
                  for item in st.session_state["cart"]
                  if item["Product"] == selected_product
              ),
              None,
          )
          if existing_item:
            existing_item["Quantity"] += qty_sold
            existing_item["Total Price"] = (
                existing_item["Quantity"] * existing_item["Unit Price"]
            )
          else:
            st.session_state["cart"].append({
                "Product": selected_product,
                "Quantity": qty_sold,
                "Unit Price": unit_price,
                "Total Price": total_price,
            })
          st.success(f"Added {selected_product} to cart!")
          st.rerun()

    if st.session_state["cart"]:
      st.markdown("### Current Bill Items")
      cart_df = pd.DataFrame(st.session_state["cart"])
      st.markdown(
          cart_df.to_html(index=False, classes="styled-table"),
          unsafe_allow_html=True,
      )

      grand_total = cart_df["Total Price"].sum()
      st.markdown(
          f"<h3 style='text-align: right; color: #ff758f;'>Grand Total:"
          f" ₹{grand_total:,.2f}</h3>",
          unsafe_allow_html=True,
      )

      not_available = st.text_input("Customer Wanted (Not Available Product)")

      col_clear, col_confirm = st.columns(2)
      with col_clear:
        if st.button("Clear Bill"):
          st.session_state["cart"] = []
          st.rerun()
      with col_confirm:
        if st.button("Confirm & Complete Sale", type="primary"):
          success_all = True
          ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
          current_date = ist_now.strftime("%Y-%m-%d")
          current_time = ist_now.strftime("%H:%M:%S")

          for item in st.session_state["cart"]:
            payload = {
                "action": "recordSale",
                "date": current_date,
                "time": current_time,
                "productName": item["Product"],
                "qtySold": int(item["Quantity"]),
                "notAvailable": not_available,
            }
            res = requests.post(WEB_APP_URL, json=payload)
            if (
                res.status_code != 200
                or res.json().get("status") != "success"
            ):
              success_all = False

          if success_all:
            st.success("All items billed and stocks updated successfully!")
            st.session_state["cart"] = []
            st.rerun()
          else:
            st.error("Some items failed to update in Google Sheets.")
    else:
      st.info("No items added to the bill yet.")
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
      ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
      payload = {
          "action": "recordPurchase",
          "date": ist_now.strftime("%Y-%m-%d"),
          "time": ist_now.strftime("%H:%M:%S"),
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
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update Google Sheet: {err_msg}")
    else:
      st.error("Please enter a valid Product Name.")

st.markdown("---")
st.subheader("Live Stocks Inventory")
if not df_stocks.empty:
  # Drop helper column before rendering the stock table
  display_df = df_stocks.drop(columns=["DISPLAY_LABEL"], errors="ignore")
  html_table = display_df.to_html(index=False, classes="styled-table")
  st.markdown(html_table, unsafe_allow_html=True)
else:
  st.info("Loading stock data from Google Sheet...")
