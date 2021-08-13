import json

from datetime import datetime

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

# run_type = "API"      # !!! Uses CMC API key and credit. Are you SURE???
# run_type = "SANDBOX" # Uses CMC sandbox and no credit.
run_type = "DEBUG"     # Uses ../data/debug_datat.json (we want this for testing).

# save_response = "NO"     # Do not save dataframe as json.
# save_response = "WRITE"  # Overwrite json file.
save_response = "APPND" # Append to json file.

data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, endpoint,
                             run_type=run_type)

# now = datetime.now().strftime("%Y%m%d_%H%M%S")
data.combine_responses(mode="a", suffix="test01")
# fn = r'C:\Users\JasonGarcia24\FINTECH-WORKSPACE\global-crypto-behavior\data\archive_latest-quotes_data_test01.csv'

# with open(fn, "r", encoding="utf-8") as f:
#     response = json.loads(f.read())

# breakpoint()
# data.json_to_dataframe(None,
#                    response=response,
#                    id=id,
#                    run_type=run_type,
#                    endpoint=endpoint
# )