import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf

# Set up the Streamlit app title with an emoji
st.title(":chart_with_upwards_trend: Stock Insights Dashboard")

# News API function
def get_news(stock_symbol):
    api_key = "a37c0b3268384a70ac0104dfffa36965"
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()

    articles = [{"title": article["title"], "description": article["description"]} 
                for article in news_data.get("articles", [])]
    return articles

# Sentiment analysis function
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score["compound"]

# Stock prediction function (simple moving average)
def predict_stock_trend(data):
    """
    Predicts next price as the average of last 5 closing prices.
    In a real application, you would use a more sophisticated model.
    """
    if "Close" in data and len(data) >= 5:
        return data["Close"].tail(5).mean()
    return None

# Stock data fetching function
def get_stock_data(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period="30d")
        return data
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

# User interface
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "AAPL")

col1, col2 = st.columns(2)

with col1:
    if st.button("Get Stock Data"):
        st.subheader(f"Stock Data for {stock_symbol}")
        stock_data = get_stock_data(stock_symbol)
        
        if stock_data is not None and not stock_data.empty:
            st.line_chart(stock_data["Close"])
            predicted_price = predict_stock_trend(stock_data)
            
            if predicted_price:
                current_price = stock_data["Close"].iloc[-1]
                trend = "↑" if predicted_price > current_price else "↓"
                st.success(f"""
                :bar_chart: Current Price: ${current_price:.2f}  
                :mag_right: Predicted Next Day Price: ${predicted_price:.2f} ({trend})
                """)

with col2:
    if st.button("Get Stock News"):
        st.subheader(f"News for {stock_symbol}")
        news_articles = get_news(stock_symbol)
        
        if news_articles:
            for article in news_articles[:5]:  # Limit to 5 articles
                if article["description"]:  # Only process articles with descriptions
                    sentiment_score = analyze_sentiment(article["description"])
                    sentiment_label = "😊 Positive" if sentiment_score > 0.05 else "😠 Negative" if sentiment_score < -0.05 else "😐 Neutral"
                    
                    with st.expander(article["title"]):
                        st.write(f"{article['description']}")
                        st.write(f"**Sentiment:** {sentiment_label} (Score: {sentiment_score:.2f})")
        else:
            st.warning("No news articles found for this stock.")

# Add some additional information and styling
st.markdown("---")
st.markdown("""
**How to use this dashboard:**
1. Enter a stock symbol (e.g., AAPL for Apple)
2. Click "Get Stock Data" to see price history and prediction
3. Click "Get Stock News" to see recent news and sentiment analysis

*Note: Predictions are based on simple moving average, not financial advice.*
""")
