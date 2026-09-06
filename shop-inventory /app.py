from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Connect to Google Sheets using credentials.json
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("inventory")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get-stocks", methods=["GET"])
def get_stocks():
    stocks_ws = sheet.worksheet("stocks")
    data = stocks_ws.get_all_records()
    return jsonify(data)

@app.route("/api/record-sale", methods=["POST"])
def record_sale():
    req = request.json
    product_name = req.get("productName")
    qty_sold = int(req.get("qtySold", 0))
    not_available = req.get("notAvailable", "")

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    stocks_ws = sheet.worksheet("stocks")
    stock_records = stocks_ws.get_all_records()

    current_stock = 0
    row_index = None
    for idx, row in enumerate(stock_records, start=2):
        if str(row.get("PRODUCT NAME")).strip().lower() == str(product_name).strip().lower():
            current_stock = int(row.get("STOCK", 0))
            row_index = idx
            break

    stock_after_sale = current_stock - qty_sold

    # Update stock tab column D (Stock)
    if row_index:
        stocks_ws.update_cell(row_index, 4, stock_after_sale)

    # Append entry to the sale tab
    sale_ws = sheet.worksheet("sale")
    sale_ws.append_row([date_str, time_str, product_name, stock_after_sale, not_available])

    return jsonify({"status": "success", "stockAfterSale": stock_after_sale})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
