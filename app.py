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

# debug = "NO"      # !!! Uses CMC API key and credit. Are you SURE???
# debug = "SANDBOX" # Uses CMC sandbox and no credit.
debug = "YES"     # Uses ../data/debug_datat.json (we want this for testing).

# save_response = "NO"     # Do not save dataframe as json.
# save_response = "WRITE"  # Overwrite json file.
save_response = "APPND" # Append to json file.

data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, endpoint,
                             save_response=save_response, debug=debug)
