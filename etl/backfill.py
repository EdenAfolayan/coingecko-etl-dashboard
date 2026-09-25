from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def insert_backfill_rows(coin_id, market_chart_response):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    rows = []
    for price_point, cap_point, vol_point in zip(
        market_chart_response.prices,
        market_chart_response.market_caps,
        market_chart_response.total_volumes
    ):
        ts_ms, price = price_point
        _, market_cap = cap_point
        _, volume = vol_point

        pulled_at = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

        rows.append((coin_id, price, market_cap, volume, pulled_at))

    query = """
        INSERT INTO coin_market_data
            (coin_id, price_usd, market_cap_usd, volume_24h_usd, pulled_at, source)
        VALUES %s
        ON CONFLICT (coin_id, pulled_at, source) DO NOTHING
    """

    psycopg2.extras.execute_values(
        cur, query, rows,
        template="(%s, %s, %s, %s, %s, 'backfill')"
    )

    conn.commit()
    cur.close()
    conn.close()