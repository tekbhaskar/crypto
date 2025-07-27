import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="🔥 Trending Crypto", layout="wide")
st.title("🚀 Trending Crypto & Trading Platforms")

@st.cache_data(ttl=300)
def get_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    coins = response.json().get("coins", [])
    trending = [
        {
            "name": c["item"]["name"],
            "coin_id": c["item"]["id"],
            "symbol": c["item"]["symbol"],
            "market_cap_rank": c["item"].get("market_cap_rank"),
            "score": c["item"].get("score")
        }
        for c in coins
    ]
    return pd.DataFrame(trending)

@st.cache_data(ttl=300)
def get_market_data(ids):
    ids_str = ",".join(ids)
    url = "https://api.coingecko.com/api/v3/coins/markets"
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

def assign_platforms(symbol):
    platforms = {
        "coinbase": ["btc", "eth", "ada", "sol", "sui"],
        "kraken": ["btc", "eth", "sol", "ada"]
    }
    result = ["Binance"]
    sym = symbol.lower()
    if sym in platforms["coinbase"]:
        result.append("Coinbase")
    if sym in platforms["kraken"]:
        result.append("Kraken")
    return ", ".join(result)

# --- Get Data ---
trending_df = get_trending_coins()
market_df = get_market_data(trending_df["coin_id"].tolist())


# --- Safe merge ---
if "id" in market_df:
    df = trending_df.merge(market_df, left_on="coin_id", right_on="id", how="left")
else:
    df = trending_df.copy()

# --- Safely handle missing columns ---
if "symbol" not in df.columns and "symbol_x" in df.columns:
    df["symbol"] = df["symbol_x"]

if "symbol" in df.columns:
    df["Trading Platforms"] = df["symbol"].apply(assign_platforms)
else:
    df["symbol"] = "N/A"
    df["Trading Platforms"] = "Unknown"

# --- Safe display ---
display_cols = ["name", "symbol", "market_cap_rank", "current_price",
                "price_change_percentage_24h", "market_cap", "Trading Platforms"]

existing_cols = [col for col in display_cols if col in df.columns]

# Rename nicely and bold headers    
col_rename = {
    "name": "Name",
    "symbol": "Symbol",
    "market_cap_rank": "Rank",
    "current_price": "Price (USD)",
    "price_change_percentage_24h": "% Change (24h)",
    "market_cap": "Market Cap",
    "Trading Platforms": "Trading Platforms"
}

def color_change_column(column):
    return [
        "color: green" if val > 0 else "color: red"
        if not pd.isna(val) else ""
        for val in column
    ]

if "% Change (24h)" in col_rename.values():
    styled_df = (
    df[existing_cols]
    .rename(columns=col_rename)
    .style
    .apply(color_change_column, subset=["% Change (24h)"] if "% Change (24h)" in col_rename.values() else [])
    .set_table_styles([{"selector": "th", "props": [("font-weight", "bold")]}])
)
else:
    styled_df = df[existing_cols].rename(columns=col_rename).style

# --- Display DataFrame ---
st.dataframe(styled_df, use_container_width=True)

# --- Manual Refresh ---
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
