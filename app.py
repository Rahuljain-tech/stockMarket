import streamlit as st
import requests
import pandas as pd
import time
import random  # To generate unique keys dynamically

# Function to fetch NSE stock price
def get_nse_stock_price(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # Establish session

    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data["priceInfo"]["lastPrice"]
            return price
        else:
            return "Failed to fetch"
    except requests.exceptions.RequestException:
        return "Network error"

# Streamlit UI Configuration
st.set_page_config(page_title="NSE Stock Price Tracker", layout="wide")
st.title("📈 NSE Stock Price Tracker")

# Initialize session state for auto-refresh control
if "running" not in st.session_state:
    st.session_state.running = False  # Default: Not running

if "stock_data" not in st.session_state:
    st.session_state.stock_data = pd.DataFrame(columns=["Stock", "Current Price (₹)"])

# User input for multiple stock symbols
stock_symbols = st.text_input("Enter NSE Stock Symbols (comma-separated, e.g., RELIANCE, TCS, INFY)", "RELIANCE, TCS, INFY")

# Convert user input into a list of stock symbols
stock_list = [symbol.strip().upper() for symbol in stock_symbols.split(",") if symbol.strip()]

# Refresh interval slider
refresh_rate = st.slider("Refresh Interval (seconds)", 5, 60, 10)

# Start & Stop buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Start Auto-Refresh"):
        st.session_state.running = True  # Start refreshing

with col2:
    if st.button("⏹ Stop Auto-Refresh"):
        st.session_state.running = False  # Stop refreshing

# Placeholder for the table
table_placeholder = st.empty()

# Function to fetch data and update only the price column
def update_prices():
    for index, row in st.session_state.stock_data.iterrows():
        stock = row["Stock"]
        new_price = get_nse_stock_price(stock)
        st.session_state.stock_data.at[index, "Current Price (₹)"] = new_price

# Initialize table only if it's empty or stocks have changed
if st.session_state.stock_data.empty or list(st.session_state.stock_data["Stock"]) != stock_list:
    st.session_state.stock_data = pd.DataFrame({"Stock": stock_list, "Current Price (₹)": ["Fetching..."] * len(stock_list)})

# Display table (use a random key to prevent DuplicateWidgetID error)
table_placeholder.data_editor(st.session_state.stock_data, use_container_width=True, disabled=["Stock"], key=f"stock_table_{random.randint(1000, 9999)}")

# Auto-refresh loop (updates only price column)
while st.session_state.running:
    time.sleep(refresh_rate)  # Wait before next update
    update_prices()  # Update only price column

    # Re-render table with updated prices
    table_placeholder.empty()  # Clear previous table to prevent duplication
    table_placeholder.data_editor(st.session_state.stock_data, use_container_width=True, disabled=["Stock"], key=f"stock_table_{random.randint(1000, 9999)}")

    st.experimental_rerun()  # Refresh UI
