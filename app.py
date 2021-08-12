from market_response.crypto import CoinMarketCapResponse
from utils.json_io          import json_write


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

# debug = "YES" # Uses ../data/debug_datat.json (we want this for testing)
debug = "NO"  # !!! Are you SURE???
# debug = "SANDBOX"

data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, endpoint, debug=debug)

print(data.dataframe.head())
breakpoint()
