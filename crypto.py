import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="🔥 Trending Crypto", layout="wide")
st.title("🚀 Today's Trending Cryptocurrencies")

@st.cache_data(ttl=300)  # cache for 5 minutes
def get_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    data = response.json()
    coins = data["coins"]
    trending = []
    for coin in coins:
        item = coin["item"]
        trending.append({
            "Name": item["name"],
            "Symbol": item["symbol"],
            "Market Cap Rank": item.get("market_cap_rank"),
            "Score": item.get("score"),
            "Coin ID": item["id"]
        })
    return pd.DataFrame(trending)

def get_market_data(ids):
    ids_str = ",".join(ids)
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids_str,
        "order": "market_cap_desc",
        "per_page": len(ids),
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

# Get trending coin data
trending_df = get_trending_coins()

# Get live market data
market_df = get_market_data(trending_df["Coin ID"].tolist())

# Merge both data sources
merged_df = trending_df.merge(market_df, left_on="Coin ID", right_on="id", how="left")

# Display with colors
def color_change(val):
    if pd.isna(val):
        return ''
    elif val > 0:
        return 'color: green'
    elif val < 0:
        return 'color: red'
    return ''

styled_df = merged_df[[
    "Name", "Symbol", "Market Cap Rank", "current_price", "price_change_percentage_24h", "market_cap"
]].rename(columns={
    "current_price": "Price (USD)",
    "price_change_percentage_24h": "% Change (24h)",
    "market_cap": "Market Cap"
}).style.applymap(color_change, subset=["% Change (24h)"])

st.dataframe(styled_df, use_container_width=True)

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
