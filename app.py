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

# COINMARKETCAP SECTION
coins        = 5000
currency     = "USD"
cmc_endpoint = "latest-quotes"
today        = datetime.now().strftime("%Y%m%d")
run_type     = "DEBUG"          # Uses ../data/debug_<endpoint>_data.csv (we want this for testing).

crypto_data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, cmc_endpoint, run_type=run_type)
crypto_df   = crypto_data.dataframe

# CRYPTO NEWS SECTION
items         = 50              # Pull 50 articles.
rank_days     = 1               # Will sort by rank for the last X days.
news_endpoint = "ticker-news"   # Define the type of data to collect (ARCHIVE_FILES).
run_type      = "DEBUG"         # Uses ../data/debug_<endpoint>_data.csv (we want this for testing).

news_df = pd.DataFrame()
for ticker in tickers:
    news_data = CryptoNewsResponse(ticker, news_endpoint, items=items, rank_days=rank_days, run_type=run_type)
    news_df   = pd.concat([news_df, news_data.dataframe])

