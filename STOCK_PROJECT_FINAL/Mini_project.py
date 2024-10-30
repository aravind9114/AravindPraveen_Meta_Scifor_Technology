import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import requests
from textblob import TextBlob

# Function to fetch stock tickers programmatically from Wikipedia (S&P 500 list)
def get_sp500_tickers():
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500_tickers[['Symbol', 'Security', 'GICS Sector']].values.tolist()

# Function to fetch news articles for a stock ticker
def get_news_sentiment(ticker):
    api_key = "da7d2bdd6951450ca90dcbf22544dd6d"  # Replace with your News API key
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}"
    response = requests.get(url).json()

    if response.get("status") != "ok":
        st.error(f"Error fetching news for {ticker}: {response.get('message', 'Unknown error')}")
        return None

    # Analyze sentiment of the news headlines
    articles = response['articles'][:5]  # Get the first 5 news articles
    news_data = []

    for article in articles:
        headline = article['title']
        sentiment = TextBlob(headline).sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        news_data.append({
            "Headline": headline,
            "Sentiment": sentiment_label
        })

    return news_data

# Function to fetch real-time stock data from Alpha Vantage
def get_real_time_data(ticker, api_key):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    response = requests.get(url).json()
    
    if "Global Quote" in response:
        data = response["Global Quote"]
        return {
            "Ticker": data["01. symbol"],
            "Current Price": float(data["05. price"]),
            "Change Percent": data["10. change percent"],
            "Volume": int(data["06. volume"])
        }
    else:
        st.error(f"Error fetching data for {ticker}: {response.get('Error Message', 'Unknown error')}")
        return None

# Create two columns for the main content
col1, col2 = st.columns([1, 2])

# Insert the image in the first column
with col1:
    st.image("https://media3.giphy.com/media/uF9QO14m402gTIVuzg/200w.gif?cid=6c09b9523emd00for8saqnyqt6yfr6m84ly382saox6yi680&ep=v1_gifs_search&rid=200w.gif&ct=g", use_column_width=True)
with col2:
    st.title("JUST START INVESTING")

# Alpha Vantage API key
alpha_vantage_api_key = "S1UXB24J79LF1G5Z"  # Replace with your Alpha Vantage API key

# Fetch dynamic list of tickers from the S&P 500
dynamic_tickers = get_sp500_tickers()

# Predefined list of popular stock tickers with company names
popular_tickers = [
    ("AAPL", "Apple Inc.", "Information Technology"),
    ("MSFT", "Microsoft Corp.", "Information Technology"),
    ("GOOGL", "Alphabet Inc. (Class A)", "Communication Services"),
    # Add more manually predefined tickers here if needed...
]

# Combine dynamic tickers with predefined tickers
combined_tickers = popular_tickers + dynamic_tickers

# Create a dictionary for quick lookup of company names
ticker_dict = {ticker: name for ticker, name, _ in combined_tickers}

# Create a list of formatted ticker names for the select box
formatted_tickers = [f"{ticker} - {name}" for ticker, name in ticker_dict.items()]

# Add a GIF to the sidebar with adjusted width
st.sidebar.image("https://media3.giphy.com/media/IrGWBZjYkVE06dvxP2/200w.gif", use_column_width=True, width=150)
st.sidebar.markdown("---")

# Filter stocks by sector
sectors = list(set([ticker[2] for ticker in combined_tickers]))
selected_sector = st.sidebar.selectbox("Filter by Sector", ["All"] + sectors)

# Multi-select dropdown for multiple stock tickers
st.sidebar.header("📌 Select Stock Tickers")
if selected_sector == "All":
    selected_tickers = st.sidebar.multiselect(
        "Choose stock tickers:", 
        formatted_tickers, 
        default=[]  # Set default to an empty list for no pre-selected tickers
    )
else:
    # Filter tickers by the selected sector
    filtered_tickers = [f"{ticker} - {name}" for ticker, name, sector in combined_tickers if sector == selected_sector]
    selected_tickers = st.sidebar.multiselect(
        "Choose stock tickers:", 
        filtered_tickers, 
        default=[]  # Set default to an empty list for no pre-selected tickers
    )

# Select the time period for fetching stock data
st.sidebar.subheader("⏳ Time Period")
period = st.sidebar.selectbox(
    "Choose time period:", 
    ["1d", "5d", "1mo", "6mo", "1y", "5y", "max"]
)

# Button to show user instructions
if st.sidebar.button("📖 Instructions"):
    st.sidebar.write("""
    ### Instructions for Using the App
    1. **Filter by Sector**: Use the dropdown to filter stocks by sector.
    2. **Select Stock Tickers**: Choose one or more stock tickers from the list.
    3. **Choose Time Period**: Select the time period for which you want to view historical data.
    4. **Compare Stocks**: Click the 'Compare Stocks' button to view stock data, charts, and news sentiment.
    5. **Download Data**: You can download the historical stock data as a CSV file for further analysis.
    """)
    
# Button to fetch and display comparison data
st.sidebar.subheader("🔎 Stock Comparison")
if st.sidebar.button("Compare Stocks"):
    st.markdown("### 📊 Stock Comparison")
    comparison_data = []

    # Individual stock display with enhanced layout and metrics
    for ticker in [ticker.split(" - ")[0] for ticker in selected_tickers]:
        try:
            stock_data = yf.Ticker(ticker)
            hist_data = stock_data.history(period=period)

            # Check if hist_data is empty
            if hist_data.empty:
                st.error(f"No historical data available for {ticker}.")
                continue

            # Use columns to create a card-like structure
            st.markdown(f"### 📈 {ticker} - {ticker_dict.get(ticker, 'Unknown Company')}")
            col1, col2, col3 = st.columns([2, 2, 1])

            # Column 1: Stock Data Table
            with col1:
                st.markdown("#### Historical Data")
                st.dataframe(hist_data)

            # Column 2: Line chart with moving averages (if enough data)
            with col2:
                st.markdown("#### Price and Moving Averages")
                if period in ["1mo", "6mo", "1y", "5y", "max"]:
                    hist_data['50_MA'] = hist_data['Close'].rolling(window=50).mean()
                    hist_data['200_MA'] = hist_data['Close'].rolling(window=200).mean()
                    st.line_chart(hist_data[['Close', '50_MA', '200_MA']])
                elif period == "5d":
                    hist_data['5_MA'] = hist_data['Close'].rolling(window=5).mean()
                    st.line_chart(hist_data[['Close', '5_MA']])
                else:
                    st.write("Not enough data to calculate moving averages.")

            # Column 3: Key Metrics
            latest_data = hist_data.iloc[-1]
            with col3:
                st.markdown("#### Key Metrics")
                latest_price = f"${latest_data['Close']:.2f}"
                week_high = f"${hist_data['Close'].max():.2f}"
                week_low = f"${hist_data['Close'].min():.2f}"

                st.metric(label="📊 Latest Price", value=latest_price)
                st.metric(label="📈 52 Week High", value=week_high)
                st.metric(label="📉 52 Week Low", value=week_low)

            # Fetch real-time data from Alpha Vantage
            real_time_data = get_real_time_data(ticker, alpha_vantage_api_key)
            if real_time_data:
                st.markdown("#### 📈 Real-Time Data")
                # Organize real-time data in a more readable format
                rt_col1, rt_col2, rt_col3 = st.columns(3)

                with rt_col1:
                    st.metric(label="Current Price", value=f"${real_time_data['Current Price']:.2f}")
                with rt_col2:
                    st.metric(label="Change Percent", value=real_time_data["Change Percent"])
                with rt_col3:
                    st.metric(label="Volume", value=f"{real_time_data['Volume']:,}")

            # Fetch news sentiment
            news_sentiment = get_news_sentiment(ticker)
            if news_sentiment:
                st.markdown("#### 📰 News Sentiment")
                for news in news_sentiment:
                    st.markdown(f"- **{news['Headline']}** - Sentiment: {news['Sentiment']}")

        except Exception as e:
            st.error(f"Error processing {ticker}: {str(e)}")

# Allow users to download the historical stock data
if selected_tickers:
    download_data = st.button("Download Historical Data")
    if download_data:
        combined_data = []
        for ticker in [ticker.split(" - ")[0] for ticker in selected_tickers]:
            stock_data = yf.Ticker(ticker)
            hist_data = stock_data.history(period=period)
            hist_data['Ticker'] = ticker
            combined_data.append(hist_data)

        # Concatenate all DataFrames into a single DataFrame
        all_data = pd.concat(combined_data)
        csv = all_data.to_csv().encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="historical_stock_data.csv", mime="text/csv")
