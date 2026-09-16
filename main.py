import os 
import time
from dotenv import load_dotenv
from coingecko_sdk import Coingecko
from live import insert_live_snapshot
from coins import upsert_coins, get_coins_without_history
from backfill import insert_backfill_rows

load_dotenv()

api_key = os.getenv("API_KEY")

client = Coingecko(
    demo_api_key=api_key,
    environment="demo"
)


def run_pipeline():
    # 1. Parent call — get current top 100
    markets_response = client.coins.markets.get(
        vs_currency="usd", order="market_cap_desc", per_page=100, page=1
    )

    coin_ids = [coin.id for coin in markets_response]

    # 2. Fill/update the coins reference table
    upsert_coins(markets_response)

    # 3. Insert this batch as live snapshot rows
    insert_live_snapshot(markets_response)

    # 4. Figure out which of these coins still need backfilling
    coins_needing_backfill = get_coins_without_history(coin_ids)

    # 5. Backfill only those
    

    for coin_id in coins_needing_backfill:
        try:
            history = client.coins.market_chart.get(
                id=coin_id, vs_currency="usd", days=30
            )
            insert_backfill_rows(coin_id, history)
            print("backfill sucessful")
        except Exception as e:
            print(f"Failed to backfill {coin_id}: {e}")
            # coin just gets picked up again next run, since it still has no backfill rows

        time.sleep(0.75)

    print("Pipeline Run Complete")

run_pipeline()


