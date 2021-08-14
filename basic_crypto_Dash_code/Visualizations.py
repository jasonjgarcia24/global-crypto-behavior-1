from market_response.crypto import CoinMarketCapResponse
from utils.json_io          import json_write
import pandas as pd

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
debug = "yes"  # !!! Are you SURE???
# debug = "SANDBOX"

data = CoinMarketCapResponse(tickers, slugs, id, coins, currency, endpoint, debug=debug)

#print(data.dataframe.head())
type(data)
dir(data)
data.url
data.print_json_dump()
#display(data)
data.dataframe
df = data.dataframe
df = df.reset_index(drop=True)
#df.head()
df["max_supply"] = df["max_supply"].fillna(0).astype(int)
df["circulating_supply"]= df["circulating_supply"].fillna(0).astype(int)
df["total_supply"]= df["total_supply"].fillna(0).astype(int)
df1 = df[['name', 'symbol','num_market_pairs',
        'last_updated', 'quote']]
print(df.columns)
display(df.dtypes)
len(df), df.count()
#df1
df_quote = pd.DataFrame(df1["quote"])
df_quote.dtypes
all = []
for x in df_quote["quote"]:
#     i = 1
    all.append(x["USD"])
    
new_df = pd.DataFrame(all)