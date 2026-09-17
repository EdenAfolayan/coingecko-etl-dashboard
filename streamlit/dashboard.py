import streamlit as st
import pandas as pd
from db import top_100_latest



# conn = psycopg2.connect(DATABASE_URL)
# cur = conn.cursor()

# query = """
#         SELECT c.name, c.symbol, cmd.price_usd, cmd.market_cap_usd
#         FROM coins as c 
#         LEFT JOIN coin_market_data as cmd ON c.coin_id = cmd.coin_id
#         WHERE cmd.source = 'live'
#         ORDER BY pulled_at DESC
# """
# cur.execute(query)
# rows = cur.fetchall()cl

# for row in rows:
#     print(f"name: {row[0]}| symbol: {row[1]}| price: {row[2]}| marketcap: {row[3]}")

columns = [
    "coin_id", "name", "symbol", "image_url", "price_usd",
    "market_cap_usd", "volume_24h_usd", "price_change_24h_pct",
    "market_cap_rank", "pulled_at"
]
df = pd.DataFrame(top_100_latest(), columns=columns)
df = df.sort_values("market_cap_rank").head(100)

numeric_cols = ["price_usd", "market_cap_usd", "volume_24h_usd", "price_change_24h_pct"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# --- Top summary row ---
st.title("Crypto Prices by Market Cap")
st.subheader("Market Summary")

total_market_cap = df["market_cap_usd"].sum()
gainer = df.loc[df["price_change_24h_pct"].idxmax()]
loser = df.loc[df["price_change_24h_pct"].idxmin()]

col1, col2, col3 = st.columns([1.5, 1, 1])

with col1:
    st.metric("Market Cap (Top 100)", f"${total_market_cap:,.0f}")

with col2:
    st.metric(
        label=f"Biggest Gainer: {gainer['name']}",
        value=f"${gainer['price_usd']:,.2f}",
        delta=f"{gainer['price_change_24h_pct']:.2f}%"
    )

with col3:
    st.metric(
        label=f"Biggest Loser: {loser['name']}",
        value=f"${loser['price_usd']:,.2f}",
        delta=f"{loser['price_change_24h_pct']:.2f}%"
    )

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top Gainers")
    gainers = (df[["image_url", "name", "symbol", "price_usd", "price_change_24h_pct"]].sort_values(by="price_change_24h_pct",ascending=False).head(3))
    st.dataframe(
        gainers.style.set_properties(subset=["price_change_24h_pct"], **{"color": "green"}),
        column_config={
                "image_url": st.column_config.ImageColumn("Logo"),
                "price_usd": st.column_config.NumberColumn("Price", format="$%.2f"),
                "price_change_24h_pct": st.column_config.NumberColumn("24h %", format="%.1f%%"),
        },
        hide_index=True,
        use_container_width=True
)

with col2:
    st.subheader("Top Losers")
    losers = (df[["image_url", "name", "symbol", "price_usd", "price_change_24h_pct"]].sort_values(by="price_change_24h_pct", ascending=True).head(3))
    st.dataframe(
        losers.style.set_properties(subset=["price_change_24h_pct"], **{"color": "red"}),
        column_config={
                "image_url": st.column_config.ImageColumn("Logo"),
                "price_usd": st.column_config.NumberColumn("Price", format="$%.2f"),
                "price_change_24h_pct": st.column_config.NumberColumn("24h %", format="%.1f%%"),
        },
        hide_index=True,
        use_container_width=True
)

st.divider()
# --- Main table ---
st.subheader("Top 100 Coins")
st.caption("Click check box to open coin detail page !")
event = st.dataframe(
    df[["image_url", "name", "symbol", "price_usd", "price_change_24h_pct", "market_cap_usd"]],
    column_config={
        "image_url": st.column_config.ImageColumn("Logo"),
        "price_usd": st.column_config.NumberColumn("Price", format="$%.2f"),
        "price_change_24h_pct": st.column_config.NumberColumn("24h %", format="%.2f%%"),
        "market_cap_usd": st.column_config.NumberColumn("Market Cap", format="$%d"),
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
)
if event.selection.rows:
    selected_index = event.selection.rows[0]
    selected_row = df.iloc[selected_index]
    selected_coin_id = df.iloc[selected_index]["coin_id"]
    st.session_state["selected_coin_id"] = selected_row["coin_id"]
    st.session_state["selected_coin_info"] = selected_row.to_dict()  # name, symbol, image_url, etc.
    st.switch_page("pages/coin_detail.py")
    


