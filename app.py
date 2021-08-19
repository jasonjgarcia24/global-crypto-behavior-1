import pandas as pd

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
# crypto_data.to_csv(mode="a", suffix=today)

crypto_df = crypto_data.dataframe

# CRYPTO NEWS SECTION
items         = 50              # Pull 50 articles.
rank_days     = 3 #1               # Will sort by rank for the last X days.
# news_endpoint = "ticker-news"   # Define the type of data to collect (ARCHIVE_FILES).
# news_endpoint = "ticker-category"   # Define the type of data to collect (ARCHIVE_FILES).
# news_endpoint = "ticker-stats"   # Define the type of data to collect (ARCHIVE_FILES).
news_endpoint = "ticker-top-mention"   # Define the type of data to collect (ARCHIVE_FILES).
search_str    = location()

# run_type = "TICKER-NEWS"       # !!! Uses Cryptonews API key and credit. Are you SURE???
# run_type = "TICKER-EVENTS"     # !!! Uses Cryptonews API key and credit. Are you SURE???
# run_type = "TICKER-CATEGORY"   # !!! Uses Cryptonews API key and credit. Are you SURE???
# run_type = "TICKER-STATS"      # !!! Uses Cryptonews API key and credit. Are you SURE???
run_type = "TICKER-TOP-MENTION"    # !!! Uses Cryptonews API key and credit. Are you SURE???
# run_type = "DEBUG"             #   Uses ../data/debug_<endpoint>_data.csv (we want this for testing).

# freq       = "D"
# date_start = pd.date_range(start="13-Aug-2021 00:00:00", end="17-Aug-2021 18:00:00", freq=freq)
# date_end   = pd.date_range(start="13-Aug-2021 23:59:59", end="17-Aug-2021 23:59:59", freq=freq)
# date_start = pd.date_range(start="13-Aug-2021 00:00:00", end="17-Aug-2021 18:00:00", freq=freq)
# date_end   = pd.date_range(start="13-Aug-2021 05:59:59", end="17-Aug-2021 23:59:59", freq=freq)

# dates  = [f"{s}-{e}" for s, e in zip(date_start.strftime('%Y%m%d'), date_end.strftime('%Y%m%d'))]
# times  = [f"{s}-{e}" for s, e in zip(date_start.strftime('%H%M%S'), date_end.strftime('%H%M%S'))]
# suffix = "last7days" #datetime.today().strftime("%Y%m%d") #f"{dates[0][:8]}-{dates[-1][:8]}"
dates  = ["08142021",]

news_df = pd.DataFrame()
# for ticker in tickers:
for date in dates:
    print(f"{dates=}")
    suffix    = pd.to_datetime(date, format="%m%d%Y").strftime("%Y%m%d")
    news_data = CryptoNewsResponse(tickers, news_endpoint, date=f"{date}-{date}", items=items, rank_days=rank_days, run_type=run_type, search_str=search_str)
    news_df   = pd.concat([news_df, news_data.dataframe])

    news_data.to_csv(mode="a", suffix=suffix)

breakpoint()
    
