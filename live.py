from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def insert_live_snapshot(markets_response):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    rows = [
        (
            coin.id,
            coin.current_price,
            coin.market_cap,
            coin.total_volume,
            coin.price_change_percentage_24h,
            coin.market_cap_rank,
            coin.last_updated,
        )
        for coin in markets_response
    ]

    query = """
        INSERT INTO coin_market_data
            (coin_id, price_usd, market_cap_usd, volume_24h_usd,
             price_change_24h_pct, market_cap_rank, pulled_at, source)
        VALUES %s
        ON CONFLICT (coin_id, pulled_at, source) DO NOTHING
    """

    psycopg2.extras.execute_values(
        cur, query, rows,
        template="(%s, %s, %s, %s, %s, %s, %s, 'live')"
    )

    conn.commit()
    cur.close()
    conn.close()