from datetime import datetime
from zoneinfo import ZoneInfo
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Bavesh Inventory", page_icon="💼", layout="wide"
)

# Professional Enterprise Billing CSS: Eliminate top gap and frame title in a clean card box
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    .stApp {
        background-color: #f4f6f9 !important;
        color: #333333 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    .stButton>button {
        background-color: #2b6cb0 !important;
        color: white !important;
        font-weight: 600;
        font-size: 14px;
        padding: 0.5rem 1.2rem;
        border-radius: 6px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2c5282 !important;
        color: white !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    h1, h2, h3, h4, h5, h6 {
        color: #1a202c !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }

    table {
        width: 100% !important;
        margin: auto;
        border-collapse: collapse;
        background-color: #ffffff;
        color: #2d3748;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    th {
        background-color: #2b6cb0 !important;
        color: white !important;
        text-align: center !important;
        padding: 14px;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    td {
        text-align: center !important;
        padding: 12px;
        border-bottom: 1px solid #edf2f7;
        font-size: 14px;
        color: #4a5568 !important;
    }
    tr:last-child td {
        border-bottom: none;
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
      """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <h2 style="color: #2b6cb0; margin: 0; font-size: 1.5rem; font-weight: 700;">Bavesh Enterprise Login</h2>
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.markdown("Please enter your credentials to access the billing dashboard.")

  with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_btn = st.form_submit_button("Sign In", type="primary")

    if submit_btn:
      if username == "bavesh" and password == "Balu@123":
        st.session_state["authenticated"] = True
        st.success("Login successful!")
        st.rerun()
      else:
        st.error("Invalid username or password.")
  st.stop()

st.markdown(
    """
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 18px;">
        <h2 style="color: #1a202c; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.01em;">
            Bavesh Inventory & Sales Management System
        </h2>
    </div>
""",
    unsafe_allow_html=True,
)


def get_stocks():
  try:
    fresh_url = f"{WEB_APP_URL}?t={time.time()}"
    response = requests.get(fresh_url)
    return response.json()
  except Exception:
    return []


stocks_data = get_stocks()
df_stocks = pd.DataFrame(stocks_data)

tab1, tab2 = st.tabs(["🛒 Multi-Item Billing Counter", "📦 Product & Stock Management"])

with tab1:
  st.subheader("Point of Sale Billing")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    # Build display option including Product Code and Product Name and Stock
    # Adjust column names based on your sheet structure ('PRODUCT ID' or 'PRODUCT CODE')
    id_col = (
        "PRODUCT ID"
        if "PRODUCT ID" in df_stocks.columns
        else ("PRODUCT CODE" if "PRODUCT CODE" in df_stocks.columns else None)
    )

    if id_col:
      df_stocks["DISPLAY_LABEL"] = (
          "["
          + df_stocks[id_col].astype(str)
          + "] "
          + df_stocks["PRODUCT NAME"]
          + " (Stock: "
          + df_stocks["STOCK"].astype(str)
          + ")"
      )
    else:
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

    col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
    with col1:
      selected_display = st.selectbox(
          "Search & Select Product (Code & Name)",
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
      if st.button("Add Item"):
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
          st.success(f"Added {selected_product} to invoice!")
          st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state["cart"]:
      st.markdown("#### Invoice Line Items")
      cart_df = pd.DataFrame(st.session_state["cart"])
      st.markdown(
          cart_df.to_html(index=False, classes="styled-table"),
          unsafe_allow_html=True,
      )

      grand_total = cart_df["Total Price"].sum()
      st.markdown(
          f"<h3 style='text-align: right; color: #e53e3e; margin-top: 15px;'>Grand"
          f" Total: ₹{grand_total:,.2f}</h3>",
          unsafe_allow_html=True,
      )

      not_available = st.text_input("Customer Wanted (Out of Stock Item Requests)")

      st.markdown("<br>", unsafe_allow_html=True)
      col_clear, col_confirm = st.columns([1, 1], gap="medium")
      with col_clear:
        if st.button("Clear Invoice"):
          st.session_state["cart"] = []
          st.rerun()
      with col_confirm:
        if st.button("Complete Transaction", type="primary"):
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
            st.success("Transaction completed and inventory synchronized!")
            st.session_state["cart"] = []
            st.rerun()
          else:
            st.error("Transaction synchronization failed with backend server.")
    else:
      st.info("No items added to current invoice.")
  else:
    st.warning("No products found in inventory repository.")

with tab2:
  st.subheader("Add New Product or Restock Purchase")
  col_p1, col_p2 = st.columns(2, gap="medium")
  with col_p1:
    new_prod_id = st.text_input("Product ID / Code (e.g., 101)")
    new_prod_name = st.text_input("Product Name")
  with col_p2:
    qty_purchased = st.number_input(
        "Quantity Purchased", min_value=1, value=1, step=1, key="p_qty"
    )
    price = st.number_input(
        "Unit Price", min_value=0.0, value=0.0, step=1.0, key="p_price"
    )

  st.markdown("<br>", unsafe_allow_html=True)
  if st.button("Submit Stock Entry", type="primary"):
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
            f"Successfully updated stock entry for {new_prod_name}!"
        )
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update database: {err_msg}")
    else:
      st.error("Please enter a valid Product Name.")

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.subheader("Live Enterprise Stock Inventory")
if not df_stocks.empty:
  display_df = df_stocks.drop(columns=["DISPLAY_LABEL"], errors="ignore")
  html_table = display_df.to_html(index=False, classes="styled-table")
  st.markdown(html_table, unsafe_allow_html=True)
else:
  st.info("Loading inventory records...")
