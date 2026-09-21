from db import single_coin_history
import pandas as pd
import streamlit as st
import plotly.express as px 
st.set_page_config(page_title="Coin Detail", layout="wide")

if "selected_coin_id" not in st.session_state:
    st.warning("No coin selected. Go back to the main page and click a coin.")
    st.stop()

coin_id = st.session_state["selected_coin_id"]
info = st.session_state["selected_coin_info"]

# --- Header section ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image(info["image_url"], width=80)
with col2:
    st.title(f"{info['name']} ({info['symbol'].upper()})")
    st.caption(f"Market Cap Rank #{int(info['market_cap_rank'])}")

col1 = st.metric("Price", f"${info['price_usd']:,.2f}", delta=f"{info['price_change_24h_pct']:.2f}%")



col2, col3 = st.columns(2)

with col2:
    st.metric("Market Cap", f"${info['market_cap_usd']:,.0f}")
with col3:
    st.metric("24h Volume", f"${info['volume_24h_usd']:,.0f}")

st.divider()


history_rows = single_coin_history(coin_id) 
history_df = pd.DataFrame(history_rows, columns=["price_usd", "pulled_at", "source"])
history_df["price_usd"] = pd.to_numeric(history_df["price_usd"], errors="coerce")

fig = px.line(history_df, x="pulled_at", y="price_usd", title=f"{info["name"]} Price History", labels={"pulled_at": "Date", "price_usd": "Price (USD)"})
st.plotly_chart(fig, use_container_width=True)
