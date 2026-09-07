from datetime import datetime
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Bavesh Inventory", page_icon="🌿", layout="wide"
)

# Professional CSS to enforce Light Theme, center text, and hide top toolbar
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f7f2 !important;
        color: #1b4d3e !important;
    }
    
    .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #1b4d3e !important;
        font-weight: 600 !important;
    }

    .stButton>button {
        background-color: #cc2929 !important;
        color: white !important;
        font-weight: 600;
        font-size: 15px;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #a31f1f !important;
        color: white !important;
    }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
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
      "<h2 style='color: #2e7d32; font-size: 1.8rem;'>Bavesh System Login</h2>",
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
    "<h1 style='text-align: center; color: #1b4d3e; font-size: 2.2rem;"
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

tab1, tab2 = st.tabs(["Record Sale", "Add New Product / Purchase"])

with tab1:
  st.subheader("Process a Customer Sale")
  if not df_stocks.empty and "PRODUCT NAME" in df_stocks.columns:
    product_list = df_stocks["PRODUCT NAME"].dropna().tolist()

    selected_product = st.selectbox(
        "Search & Select Product (Type to filter)",
        options=product_list,
        key="sale_prod_name",
    )

    matched_row = df_stocks[df_stocks["PRODUCT NAME"] == selected_product]

    if not matched_row.empty:
      st.info(
          f"Selected: **{selected_product}** | Available Stock: **"
          f" {matched_row['STOCK'].values[0] if 'STOCK' in matched_row.columns else 'N/A'}"
          "**"
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
        st.rerun()
      else:
        err_msg = res_json.get("message", "Unknown error")
        st.error(f"Failed to update Google Sheet: {err_msg}")
    else:
      st.error("Please enter a valid Product Name.")

st.markdown("---")
st.subheader("Live Stocks Inventory")
if not df_stocks.empty:
  # Apply Pandas Styler to center-align both headers and data cells
  styled_df = (
      df_stocks.style.set_properties(**{"text-align": "center"})
      .set_table_styles(
          [
              {
                  "selector": "th",
                  "props": [
                      ("text-align", "center"),
                      ("background-color", "#1b4d3e"),
                      ("color", "white"),
                  ],
              }
          ]
      )
      .hide(axis="index")
  )
  st.markdown(styled_df.to_html(), unsafe_allow_html=True)
else:
  st.info("Loading stock data from Google Sheet...")
