import pandas   as pd
import datetime as DT

from datetime import datetime

from utils.search_string    import location
from market_response.crypto import CoinMarketCapResponse
from media_response.news    import CryptoNewsResponse


cryptocurrencies = {
    "Bitcoin":  ("BTC", "1"),
    "Ethereum": ("ETH", "1027"),
    "Cardano":  ("ADA", "2010"),
    "Litecoin": ("LTC", "2"),
    "Monero":   ("XMR", "328"),
    "Dogecoin": ("DOGE", "74"),
}

slugs, tickers, id = list(zip(*[[x, y, z] for x, (y, z) in cryptocurrencies.items()]))

# COINMARKETCAP SECTION
coins        = 5000
currency     = "USD"
cmc_endpoint = "latest-quotes"
today        = datetime.now().strftime("%Y%m%d")

# run_type = "API"                # !!! Uses CMC API key and credit. Are you SURE???
# run_type = "SANDBOX"            # Uses CMC sandbox and no credit.
run_type = "DEBUG"              # Uses ../data/debug_<endpoint>_data.csv (we want this for testing).

crypto_data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, cmc_endpoint, run_type=run_type)
crypto_data.to_csv(mode="a", suffix=today)

crypto_df = crypto_data.dataframe

# CRYPTO NEWS SECTION
items         = 50               # Pull 50 articles.
rank_days     = 3                # Will sort by rank for the last X days.
news_endpoint = "ticker-news"    # Define the type of data to collect (ARCHIVE_FILES).
run_type = "TICKER-NEWS"         # !!! Uses Cryptonews API key and credit. Are you SURE???

time_formatter = lambda t: t.strftime("%Y%m%d")
today = DT.datetime.now()

for page in range(1, 4):
    for day in range(14, 22):
        collection_switch = {
            ("ticker-top-mention", "TICKER-TOP-MENTION"): {
                "date": f"{time_formatter(today-DT.timedelta(days=7))}-{time_formatter(today)}",
                "run_type": "TIKER-MENTION",
                "save_csv": None,
                },
            ("ticker-stats", "TICKER-STATS"): {
                "date": "last7days",
                "run_type": "TICKER-STATS",
                "save_csv": None,
                },
            ("ticker-news", "TICKER-NEWS"): {
                "date": f"202108{day}",
                "items": 50,
                "rank_days": 1,
                "run_type": "TICKER-NEWS",
                "save_csv": None,
                "page": page,
                },
        }

        # Collect news:
        collection = collection_switch.get((news_endpoint, run_type))
        news_data  = CryptoNewsResponse(tickers, news_endpoint, **collection)
        suffix     = collection["date"]

        news_data.to_csv(mode="a", suffix=suffix)

