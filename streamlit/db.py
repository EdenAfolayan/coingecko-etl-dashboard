from dotenv import load_dotenv
import os
import psycopg2
import streamlit as st

load_dotenv()

def get_secret(key):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

DATABASE_URL = get_secret("DATABASE_URL")

@st.cache_resource
def get_connection():
    return psycopg2.connect(DATABASE_URL)

def get_live_connection():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        get_connection.clear()
        conn = get_connection()
    return conn

st.cache_data(ttl=60)
def top_100_latest():
    conn = get_live_connection()
    cur = conn.cursor()
    query = """
        SELECT DISTINCT ON (coin_id)
                c.coin_id,
                c.name,
                c.symbol,
                c.image_url,
                cmd.price_usd,
                cmd.market_cap_usd,
                cmd.volume_24h_usd,
                cmd.price_change_24h_pct,
                cmd.market_cap_rank,
                cmd.pulled_at
        FROM coins as c 
        LEFT JOIN coin_market_data as cmd ON c.coin_id = cmd.coin_id
        WHERE cmd.source = 'live'
        ORDER BY c.coin_id, cmd.pulled_at DESC
        """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()

    return rows

st.cache_data(ttl=60)
def single_coin_history(selected_coin):
    conn = get_live_connection()
    cur = conn.cursor()

    query = """
        SELECT price_usd, pulled_at, source
        FROM coin_market_data
        WHERE coin_id = %s
        ORDER BY pulled_at
        """
    cur.execute(query, (selected_coin,))
    rows = cur.fetchall()
    cur.close()

    return rows