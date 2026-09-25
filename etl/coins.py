import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def upsert_coins(markets_response):
    """
    Takes the response from client.coins.markets.get() and
    inserts new coins / updates existing ones in the `coins` table.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    query = """
        INSERT INTO coins (coin_id, symbol, name, image_url, last_seen)
        VALUES %s
        ON CONFLICT (coin_id)
        DO UPDATE SET
            symbol = EXCLUDED.symbol,
            name = EXCLUDED.name,
            image_url = EXCLUDED.image_url,
            last_seen = now()
    """

    psycopg2.extras.execute_values(
        cur,
        query,
        [(coin.id, coin.symbol, coin.name, coin.image) for coin in markets_response],
        template="(%s, %s, %s, %s, now())"
    )

    conn.commit()
    cur.close()
    conn.close()

def get_coins_without_history(coin_ids):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT coin_id
        FROM coin_market_data
        WHERE source = 'backfill'
    """)
    already_backfilled = {row[0] for row in cur.fetchall()}  # a set, for fast lookup

    cur.close()
    conn.close()

    return [cid for cid in coin_ids if cid not in already_backfilled]