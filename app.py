import base64
import time
import nest_asyncio
import streamlit as st
import asyncio
import datetime

from data_fetchers.stock_data_handler.stock_data_handler import StockDataHandler
from logic.download_data.download_data import HistoricalDataDownloader
from utils.remove_streamlit_logo_and_footer import remove_streamlit_logo_and_footer
from utils.set_black_background import set_black_background
from constants.nifty_50_stock_symbols import NIFTY_50_STOCKS
from streamlit_autorefresh import st_autorefresh
from logging_config import logger


# Allow nested event loops (needed for async code in Streamlit)
nest_asyncio.apply()

# --------------------------------------------
# Initialize session state for download dates
# --------------------------------------------
if "download_start_date" not in st.session_state:
    st.session_state["download_start_date"] = datetime.date.today() - datetime.timedelta(days=30)
if "download_end_date" not in st.session_state:
    st.session_state["download_end_date"] = datetime.date.today()

# ----------------------------------------
# Page Configuration & Global Styling
# ----------------------------------------
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    layout="wide",
    page_icon="💹"
)
remove_streamlit_logo_and_footer()
set_black_background()

logger.info("Page configured and styling applied.")

# ---------------------------------------
# Sidebar: Stock Selection & Parameters
# ---------------------------------------
st.sidebar.header("⚡ Stock Selection")
selected_stock = st.sidebar.selectbox("Select NIFTY 50 Stock", list(NIFTY_50_STOCKS.keys()))
manual_stock_input = st.sidebar.text_input("Or enter a different stock symbol (e.g., TSLA, AAPL)").strip().upper()
ticker_symbol = manual_stock_input if manual_stock_input else NIFTY_50_STOCKS[selected_stock]

st.sidebar.header("⏳ Interval & Refresh")
interval = st.sidebar.selectbox("Select Interval", ["1min", "5min", "15min", "30min", "60min"])
refresh_rate = st.sidebar.slider("Auto Refresh (Seconds)", 0, 60, 10)

st.sidebar.header("📊 Select Indicators")
selected_indicators = st.sidebar.multiselect(
    "Choose Indicators to Display on Chart",
    ["RSI 14", "RSI 9", "CCI 20", "ADX 20", "WaveTrend 1", "WaveTrend 2"],
    default=[]
)

logger.info("Sidebar configured. Ticker: %s, Interval: %s, Indicators: %s", ticker_symbol, interval, selected_indicators)

# -----------------------------------
# Tabs: Chart & Download Section
# -----------------------------------
tab_chart, tab_download = st.tabs(["📈 Chart", "📥 Download Historical Data"])

# --------------------------------------
# Async Runner Helper (for async calls)
# --------------------------------------
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# -----------------------------------
# 📈 Chart Tab (Auto-Refresh)
# -----------------------------------
with tab_chart:
    st.title(f"📈 {ticker_symbol} - Real-Time Dashboard")
    logger.info("Chart tab activated for ticker %s", ticker_symbol)

    # Enable auto-refresh only on the chart tab
    if refresh_rate > 0:
        st_autorefresh(interval=refresh_rate * 1000, key="chart_autorefresh")
        logger.info("Auto-refresh enabled with interval %s seconds", refresh_rate)

    # Display last updated time
    time_placeholder = st.empty()

    def update_time():
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        time_placeholder.markdown(f"🕒 **Last updated:** {current_time}")
        logger.debug("Displayed last updated time: %s", current_time)

    # Initialize StockDataHandler and fetch data
    stock_data_handler = StockDataHandler(ticker_symbol, interval, selected_indicators)

    async def update_stock_data():
        await stock_data_handler.fetch_and_plot_data()
        logger.info("Stock data updated and chart plotted for %s", ticker_symbol)

    run_async(update_stock_data())
    update_time()

# -----------------------------------
# 📥 Download Tab (Persistent Panel)
# -----------------------------------
with tab_download:
    st.title("📥 Download Historical Data")
    logger.info("Download tab activated for ticker %s", ticker_symbol)

    # Persistent date input
    start_date = st.date_input(
        "Start Date",
        value=st.session_state["download_start_date"],
        key="download_start_date"
    )
    end_date = st.date_input(
        "End Date",
        value=st.session_state["download_end_date"],
        key="download_end_date"
    )

    if st.button("Download Data"):
        if not ticker_symbol:
            st.error("⚠️ Please select a stock symbol.")
            logger.error("Download error: No ticker symbol selected.")
        elif start_date >= end_date:
            st.error("⚠️ End date must be after start date.")
            logger.error("Download error: Invalid date range. Start: %s, End: %s", start_date, end_date)
        else:
            with st.status("📥 Fetching historical data, please wait...", expanded=True) as status:
                downloader = HistoricalDataDownloader(ticker_symbol, str(start_date), str(end_date))
                excel_data = asyncio.run(downloader.generate_excel_file())

                if excel_data:
                    status.update(label="✅ Download Ready!", state="complete", expanded=False)
                    logger.info("Historical data downloaded successfully for %s", ticker_symbol)
                    # Convert file bytes to a base64-encoded download link.
                    b64 = base64.b64encode(excel_data).decode()
                    href = (
                        f'<a href="data:application/octet-stream;base64,{b64}" '
                        f'download="{ticker_symbol}_historical_data.xlsx">📥 Click here to download</a>'
                    )
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    status.update(label="⚠️ Failed to fetch historical data. Please try again.", state="error")
                    logger.error("Failed to generate Excel file for historical data of %s", ticker_symbol)
