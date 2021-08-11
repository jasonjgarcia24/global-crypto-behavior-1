from market_response.crypto import CoinMarketCapResponse
from utils.json_io          import json_write


cryptocurrencies = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "Cardano": "ADA",
    "Litecoin": "LTC",
    "Ripple": "XRP",
    "Monero": "XMR",
    "Dogecoin": "DOGE"
}

slugs, tickers = list(zip(*cryptocurrencies.items()))
coins          = 5000
currency       = "USD"

endpoint       = "info"             # Metadata
# endpoint       = "listings/latest"  # Latest listing data

# debug = "YES" # Uses ../data/debug_datat.json (we want this for testing)
# debug = "NO"  # !!! Are you SURE???
debug = "SANDBOX"

data = CoinMarketCapResponse(tickers, slugs,  coins, currency, endpoint,
                             make_request=True, debug=debug)



breakpoint()
