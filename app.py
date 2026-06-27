import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.title("🚀 PulseInvest AI")
st.caption(
    "An AI-powered investment intelligence platform for retail investors"
)

# ----------------------------
# THEME (BLACK + PINK + BLUE)
# ----------------------------
st.markdown("""
<style>

.stApp {
    background-color: #0a0a0a;
    color: white;
}

/* Titles */
h1, h2, h3 {
    color: #ffffff !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 2px solid #00bcd4;
}

/* Inputs */
input {
    background-color: #1a1a1a !important;
    color: white !important;
    border: 1px solid #ff4fa3 !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background-color: #111111;
    border: 1px solid #00bcd4;
    padding: 12px;
    border-radius: 10px;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #ff4fa3;
    border-radius: 10px;
}

/* Divider */
hr {
    border: 1px solid #222;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# TITLE
# ----------------------------
st.title("📊 AI Investment Decision Dashboard")

# ----------------------------
# DATA LOADER
# ----------------------------
@st.cache_data(ttl=3600)
def load_data(ticker):
    return yf.download(ticker, period="1y", progress=False)

def get_stock_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        headlines = []
        for item in news[:5]:
            headlines.append({
                "title": item.get("title", "No title"),
                "link": item.get("link", ""),
                "publisher": item.get("publisher", "")
            })

        return headlines
    except:
        return []

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("Controls")

ticker = st.sidebar.text_input("Stock Symbol", "AAPL").upper().strip()

comparison_stocks = st.sidebar.multiselect(
    "Compare Stocks",
    ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL"]
    
)
investment = st.sidebar.number_input(
    "💰 Initial Investment ($)",
    min_value=100,
    max_value=1000000,
    value=10000,
    step=100
)

# ----------------------------
# LOAD DATA
# ----------------------------
data = load_data(ticker)

if data.empty:
    st.error("No data found. Check ticker symbol.")
    st.stop()

data = data.dropna()
# Moving Averages
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

# ----------------------------
# SAFE PRICE FIX
# ----------------------------
latest_price = data["Close"].dropna().iloc[-1].item()
# ----------------------------
# COMPANY INFO
#

# ----------------------------
# RETURNS + VOLATILITY
# ----------------------------
returns = data["Close"].pct_change().dropna()

volatility = float(np.std(returns) * np.sqrt(252))
risk_free_rate = 0.05

annual_return = returns.mean() * 252

sharpe_ratio = (
    annual_return - risk_free_rate
) / volatility

data["Rolling Volatility"] = (
    data["Close"].pct_change().rolling(20).std() * np.sqrt(252)
)

# ----------------------------
# RISK LABEL
# ----------------------------
if volatility < 0.15:
    risk = "🟢 Low Risk"
elif volatility < 0.30:
    risk = "🟡 Moderate Risk"
else:
    risk = "🔴 High Risk"

# ----------------------------
# HEADER METRICS
# ----------------------------
col1, col2, col3, col4 = st.columns(4)
col4.metric(
    "Sharpe Ratio",
    f"{sharpe_ratio:.2f}"
)
cumulative = (1 + returns).cumprod()

rolling_max = cumulative.cummax()

drawdown = (
    cumulative - rolling_max
) / rolling_max

max_drawdown = drawdown.min()
st.metric(
    "Max Drawdown",
    f"{max_drawdown:.2%}"
)

col1.metric("Price", f"${latest_price:.2f}")
col2.metric("Volatility", f"{volatility:.2%}")
col3.metric("Risk", risk)

# ----------------------------
# CHARTS
# ----------------------------
st.subheader("📈 Price Trend")
st.line_chart(data["Close"])
st.line_chart(data[["Close", "MA20", "MA50"]])
st.subheader("📉 Volatility Trend")
st.line_chart(data["Rolling Volatility"])

# ----------------------------
# INVESTMENT INSIGHT PANEL
# ----------------------------
st.subheader("🧠 Investment Insight Panel")
st.subheader("🤖 AI Recommendation")

if sharpe_ratio > 1.2 and volatility < 0.30:
    st.success("BUY")

elif sharpe_ratio > 0.5:
    st.info("HOLD")

else:
    st.error("HIGH RISK")

st.markdown(f"""
### About {ticker}

This system analyzes **{ticker}** using 1-year market data.

- Current Price: **${latest_price:.2f}**
- Annual Volatility: **{volatility:.2%}**
- Risk Level: **{risk}**

Market behavior indicates:
**{'High fluctuation and trading opportunities' if volatility > 0.3 else 'Balanced movement with moderate risk' if volatility > 0.15 else 'Stable low-volatility behavior'}**
""")

# ----------------------------
# PROS & CONS
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Pros")

    if volatility < 0.15:
        st.write("• Stable price movement")
        st.write("• Lower downside risk")
    elif volatility < 0.30:
        st.write("• Balanced volatility")
        st.write("• Moderate trading opportunities")
    else:
        st.write("• High movement → trading opportunities")
        st.write("• Strong momentum potential")

    st.write("• Highly liquid stock")
    st.write("• Large market participation")

with col2:
    st.markdown("### ⚠️ Cons")

    if volatility < 0.15:
        st.write("• Limited short-term gains")
        st.write("• Slow growth periods")
    elif volatility < 0.30:
        st.write("• Moderate uncertainty")
        st.write("• Needs monitoring")
    else:
        st.write("• High risk of sharp drops")
        st.write("• Not suitable for conservative investors")

    st.write("• External news can impact price heavily")

# ----------------------------
# DISCLAIMER
# ----------------------------
st.markdown("### 🧠 Things to Remember")

st.info("""
- This is an analytical tool, not financial advice.
- Volatility measures risk, not guaranteed return.
- Always combine with fundamental research.
- News and macro events can override historical patterns.
""")

# ----------------------------
# NEWS SECTION
# ----------------------------
st.subheader("📰 Latest News")

news = get_stock_news(ticker)

if news:
    for item in news:
        st.markdown(f"""
**{item['title']}**  
🏢 {item['publisher']}  
🔗 {item['link']}

---
""")
else:
    st.write("No recent news found.")

# ----------------------------
# STOCK COMPARISON
# ----------------------------
results = []

for stock in comparison_stocks:
    df = load_data(stock)

    if df.empty:
        continue

    df = df.dropna()
    r = df["Close"].pct_change().dropna()

    v = float(np.std(r) * np.sqrt(252))

    results.append({
        "Stock": stock,
        "Volatility (%)": round(v * 100, 2)
    })

if results:
    st.subheader("📊 Stock Comparison")

    df_comp = pd.DataFrame(results)
    df_comp = df_comp.sort_values("Volatility (%)", ascending=False)

    st.dataframe(df_comp, use_container_width=True)
    with st.expander("📚 Learn Investing"):
        st.markdown("""
### Volatility
Measures how much prices fluctuate.

### Sharpe Ratio
Measures return earned for each unit of risk.

### Maximum Drawdown
Largest historical decline.

### Value at Risk
Estimated worst daily loss at a chosen confidence level.

### Moving Average
Smooths price data to identify trends.

### Diversification
Owning multiple assets can reduce portfolio risk because different investments often don't move exactly together.
""")