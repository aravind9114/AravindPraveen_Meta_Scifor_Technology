import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import requests
from textblob import TextBlob
import plotly.graph_objects as go


st.warning("For the best experience, please switch to light mode.")


# Function to fetch stock tickers programmatically from Wikipedia (S&P 500 list)
def get_sp500_tickers():
    sp500_tickers = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )[0]
    return sp500_tickers[["Symbol", "Security", "GICS Sector"]].values.tolist()


# Function to fetch news articles for a stock ticker
def get_news_sentiment(ticker):
    api_key = "da7d2bdd6951450ca90dcbf22544dd6d"  
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}&domains=forbes.com,wsj.com,reuters.com"
    response = requests.get(url).json()

    if response.get("status") != "ok":
        st.error(
            f"Error fetching news for {ticker}: {response.get('message', 'Unknown error')}"
        )
        return None

    # Analyze sentiment of the news headlines
    articles = response["articles"][:5]  # Get the first 5 news articles
    news_data = []

    for article in articles:
        headline = article["title"]
        sentiment = TextBlob(headline).sentiment.polarity
        sentiment_label = (
            "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        )
        news_data.append({"Headline": headline, "Sentiment": sentiment_label})

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
            "Volume": int(data["06. volume"]),
        }
    else:
        # st.error(f"Error fetching data for {ticker}: {response.get('Error Message', 'Unknown error')}")
        return None


# Create two columns
col1, col2 = st.columns([1, 2])  

# Insert the image in the first column
with col1:
    st.image(
        "https://media3.giphy.com/media/uF9QO14m402gTIVuzg/200w.gif?cid=6c09b9523emd00for8saqnyqt6yfr6m84ly382saox6yi680&ep=v1_gifs_search&rid=200w.gif&ct=g",
        use_column_width=True,
    )
with col2:
    st.title("JUST START INVESTING")
# Alpha Vantage API key
alpha_vantage_api_key = "S1UXB24J79LF1G5Z"  

# Fetch dynamic list of tickers from the S&P 500
dynamic_tickers = get_sp500_tickers()

# Predefined list of popular stock tickers with company names
popular_tickers = [
    ("AAPL", "Apple Inc.", "Information Technology"),
    ("MSFT", "Microsoft Corp.", "Information Technology"),
    ("GOOGL", "Alphabet Inc. (Class A)", "Communication Services"),
    
]

# Combine dynamic tickers with predefined tickers
combined_tickers = popular_tickers + dynamic_tickers

# Create a dictionary for quick lookup of company names
ticker_dict = {ticker: name for ticker, name, _ in combined_tickers}

# Create a list of formatted ticker names for the select box
formatted_tickers = [f"{ticker} - {name}" for ticker, name in ticker_dict.items()]

# Add a GIF to the sidebar with adjusted width
st.sidebar.image(
    "https://media3.giphy.com/media/IrGWBZjYkVE06dvxP2/200w.gif",
    use_column_width=True,
    width=150,
)  # Adjust width as needed
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
        default=[],  
    )
else:
    # Filter tickers by the selected sector
    filtered_tickers = [
        f"{ticker} - {name}"
        for ticker, name, sector in combined_tickers
        if sector == selected_sector
    ]
    selected_tickers = st.sidebar.multiselect(
        "Choose stock tickers:",
        filtered_tickers,
        default=[],  # 
    )

# Select the time period for fetching stock data
st.sidebar.subheader("⏳ Time Period")
period = st.sidebar.selectbox(
    "Choose time period:", ["1d", "5d", "1mo", "6mo", "1y", "5y", "max"]
)

# Button to fetch and display comparison data
st.sidebar.subheader("🔎 Stock Comparison")
if st.sidebar.button("Compare Stocks"):
    # st.markdown("### 📊 Stock Comparison")
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
            st.markdown(
                f"### 📈 {ticker} - {ticker_dict.get(ticker, 'Unknown Company')}"
            )
            st.markdown("### 🗃️ Historical Data")
            st.markdown(
                f"""
            <div style='
                border: 1px solid #d4d4d4;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #f9f9f9;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                max-height: 400px;
                overflow-y: auto;
            '>
                {hist_data.to_html(classes='table table-striped', index=False)}
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown("### 📊 Price and Moving Averages")
            if period in ["1mo", "6mo", "1y", "5y", "max"]:
                hist_data["50_MA"] = hist_data["Close"].rolling(window=50).mean()
                hist_data["200_MA"] = hist_data["Close"].rolling(window=200).mean()
                st.line_chart(hist_data[["Close", "50_MA", "200_MA"]])
            elif period == "5d":
                hist_data["5_MA"] = hist_data["Close"].rolling(window=5).mean()
                st.line_chart(hist_data[["Close", "5_MA"]])
            else:
                st.markdown(
                    "<div style='text-align: center; color: red;'>Not enough data to calculate moving averages.</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("### 📈 Key Metrics")
            latest_data = hist_data.iloc[-1]
            latest_price = f"${latest_data['Close']:.2f}"
            week_high = f"${hist_data['Close'].max():.2f}"
            week_low = f"${hist_data['Close'].min():.2f}"

            st.markdown(
                f"""
        <div style='display: flex; flex-direction: column; gap: 20px;'>
            <div style='
                border: 1px solid #d4d4d4;
                border-radius: 10px;
                padding: 15px;
                background-color: #f9f9f9;
                text-align: center;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            '>
                <h4 style='margin-bottom: 5px;'>💰 Latest Price</h4>
                <p style='margin: 0;'>{latest_price}</p>
            </div>
            <div style='
                border: 1px solid #d4d4d4;
                border-radius: 10px;
                padding: 15px;
                background-color: #f9f9f9;
                text-align: center;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            '>
                <h4 style='margin-bottom: 5px;'>🔝 52 Week High</h4>
                <p style='margin: 0;'>{week_high}</p>
            </div>
            <div style='
                border: 1px solid #d4d4d4;
                border-radius: 10px;
                padding: 15px;
                background-color: #f9f9f9;
                text-align: center;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            '>
                <h4 style='margin-bottom: 5px;'>🔻 52 Week Low</h4>
                <p style='margin: 0;'>{week_low}</p>
            </div>
        </div>
        """,
                unsafe_allow_html=True,
            )

            

            # Fetch real-time data from Alpha Vantage
            real_time_data = get_real_time_data(ticker, alpha_vantage_api_key)
            if real_time_data is None:
                st.warning(
                    "Real-time data is currently unavailable because the market is closed. Please check back during market hours for the most up-to-date information."
                )
            else:
                st.markdown("### 📈 Real-Time Data")
                st.markdown(
                    f"""
                <div style='display: flex; flex-direction: row; justify-content: space-around; gap: 20px; margin-top: 20px;'>
                    <div style='
                        border: 1px solid #d4d4d4;
                        border-radius: 10px;
                        padding: 15px;
                        background-color: #f9f9f9;
                        text-align: center;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                        flex: 1;
                    '>
                        <h5 style='margin-bottom: 5px;'>💰 Current Price</h5>
                        <p style='margin: 0;'>{f"${real_time_data['Current Price']:.2f}"}</p>
                    </div>
                    <div style='
                        border: 1px solid #d4d4d4;
                        border-radius: 10px;
                        padding: 15px;
                        background-color: #f9f9f9;
                        text-align: center;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                        flex: 1;
                    '>
                        <h5 style='margin-bottom: 5px;'>📈 Change</h5>
                        <p style='margin: 0; color: {"green" if float(real_time_data["Change Percent"].strip("%")) >= 0 else "red"};'>
                            {f"{real_time_data['Change Percent']}"}
                        </p>
                    </div>
                    <div style='
                        border: 1px solid #d4d4d4;
                        border-radius: 10px;
                        padding: 15px;
                        background-color: #f9f9f9;
                        text-align: center;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                        flex: 1;
                    '>
                        <h5 style='margin-bottom: 5px;'>📊 Volume</h5>
                        <p style='margin: 0;'>{f"{real_time_data['Volume']:,}"}</p>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("#### 📉 Candlestick Chart")

            # Create a Plotly candlestick chart
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=hist_data.index,
                        open=hist_data["Open"],
                        high=hist_data["High"],
                        low=hist_data["Low"],
                        close=hist_data["Close"],
                        name=ticker,
                        increasing_line_color="green",
                        decreasing_line_color="red",
                    )
                ]
            )

            # Update layout
            fig.update_layout(
                title=f"{ticker} ({ticker_dict[ticker]}) Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=True,
                template="plotly_white",
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig)

            # Download button section with defined ticker
            st.download_button(
                label=f"Download {ticker} data as CSV",
                data=hist_data.to_csv(),
                file_name=f"{ticker}_stock_data.csv",
                mime="text/csv",
            )

            # Fetch and display news sentiment for the selected ticker
            st.markdown(f"### 📰 News Sentiment for {ticker}")

            news_sentiment_data = get_news_sentiment(ticker)
            if news_sentiment_data:
                for news in news_sentiment_data:
                    st.markdown(
                        f"""
                    <div style='
                        border: 1px solid #d4d4d4;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 15px 0;
                        background-color: #f9f9f9;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    '>
                        <h4 style='margin-bottom: 10px;'>📌 {news['Headline']}</h4>
                        <p style='margin: 0;'><strong>Sentiment:</strong> {news['Sentiment']}</p>
                        <small><em>Source: Your Trusted News API</em></small>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        except Exception as e:
            st.error(f"Error processing data for {ticker}: {e}")
import streamlit as st

# Sidebar for user instructions
st.sidebar.header("User Instructions")

# Add a button for users to understand how to read the candlestick chart
if st.sidebar.button("📖 How to Read Candlestick Charts"):
    st.markdown(
        """
    ### How to Read Candlestick Charts

    Candlestick charts provide a visual representation of price movements for a stock over a specific period. Each candlestick shows four key price points:
    
    - **Open**: The price at which the stock opened for that time period.
    - **High**: The highest price reached during the time period.
    - **Low**: The lowest price reached during the time period.
    - **Close**: The price at which the stock closed for that time period.

    The body of the candlestick is filled or colored based on whether the stock closed higher or lower than it opened:
    
    - **Green (or filled)**: Indicates the stock closed higher than it opened (bullish).
    - **Red (or hollow)**: Indicates the stock closed lower than it opened (bearish).

    **Wicks** (the lines extending from the top and bottom of the body) show the high and low prices for that period. A long wick can indicate a potential reversal or volatility.

    **Key Points to Remember**:
    - Multiple green candles in succession can indicate strong buying pressure.
    - Multiple red candles can indicate strong selling pressure.
    - Candlestick patterns, like dojis or hammers, can provide insights into potential market reversals.

    Understanding these basics can help you analyze market trends and make informed investment decisions!
    """
    )

# Add a button for users to understand how to use the app
if st.sidebar.button("📖 How to Use This App"):
    st.markdown(
        """
    ### How to Use This App

    This app provides a comprehensive tool for stock market analysis and investment research. Here’s a guide on how to navigate through its features:

    #### 1. **Select Stock Tickers**
    - Use the **"Select Stock Tickers"** section in the sidebar to choose from a list of stock tickers.
    - You can filter stocks by sector using the **"Filter by Sector"** dropdown.
    - The multi-select dropdown allows you to choose multiple stock tickers at once.

    #### 2. **Choose Time Period**
    - In the **"Time Period"** section, select how far back you want to view the stock data (e.g., 1 day, 5 days, 1 month, etc.).

    #### 3. **Compare Stocks**
    - Click the **"Compare Stocks"** button to generate a detailed comparison of the selected stock tickers.
    - You will see a combination of historical data, price trends, key metrics, and real-time data for each selected stock.

    #### 4. **Analyze Historical Data**
    - Each stock's historical data will be displayed in a table format, showing the stock prices over the chosen time period.

    #### 5. **View Price Trends**
    - The app includes line charts and candlestick charts to visualize stock price movements and patterns.
    - Moving averages are also calculated to help identify trends.

    #### 6. **Download Stock Data**
    - Use the **"Download"** button to save the historical stock data as a CSV file for further analysis.

    #### 7. **News Sentiment Analysis**
    - Stay updated with the latest news headlines related to the selected stocks.
    - The app analyzes the sentiment of these headlines, indicating whether they are positive, negative, or neutral.

    ### Conclusion
    This app aims to provide you with the tools you need to make informed investment decisions. Explore the data, visualize trends, and stay updated with news sentiments to enhance your investment strategy!
    """
    )
st.sidebar.markdown("---")
st.sidebar.markdown("### Developed by Aravind Praveen")
st.sidebar.markdown("Providing insights for informed investment decisions.")

alpha_vantage_api_key = "S1UXB24J79LF1G5Z"
api_key = "da7d2bdd6951450ca90dcbf22544dd6d"
