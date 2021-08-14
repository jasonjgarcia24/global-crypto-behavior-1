import pandas as pd

from datetime import datetime

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

coins    = 5000
currency = "USD"
endpoint = "latest-quotes"

# run_type = "API"      # !!! Uses CMC API key and credit. Are you SURE???
# run_type = "SANDBOX" # Uses CMC sandbox and no credit.
run_type = "DEBUG"     # Uses ../data/debug_datat.json (we want this for testing).

crypto_data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, endpoint,
                                    run_type=run_type)

crypto_data.combine_responses(mode="w", suffix="MANUAL-RUN")

# run_type = "API"     # Uses ../data/debug_datat.json (we want this for testing).
run_type = "DEBUG"     # Uses ../data/debug_datat.json (we want this for testing).

news_data = CryptoNewsResponse(ticker, items=50, endpoint="", rank_days=1,
                               run_type=run_type)
