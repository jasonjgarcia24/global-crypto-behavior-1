# Import the required libraries and dependencies
import os
import re
import urllib
import json

import pandas as pd

from dotenv   import load_dotenv
from requests import Session

from collections.abc     import Iterable
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


class Investment:
    load_dotenv()

    YEARLY_TRADING_DAYS = 252
    INVESTMENT_TYPES = {
        "CoinMarketCapResponse": "crypto",
        "AlpacaBarset":          "shares"
    }
    INVESTMENT_TYPES_STR = "|".join(INVESTMENT_TYPES.keys())

    def __init__(self, ticker: str, name: str, id: Iterable, count: float, currency: str):
        self.ticker      = ticker
        self.name        = name
        self.id          = id
        self.__count     = count
        self.currency    = currency
        self.__response  = None


class CoinMarketCapResponse(Investment):
    ARCHIVE_FILES = {
            "metadata":        "metadata_data.json",
            "latest-listings": "latest-listing_data.json",
            "latest-quotes":   "latest-quotes_data.json",
    }

    RUN_TYPE_OPTIONS = ["API", "SANDBOX", "DEBUG"]
        
    URL_SWITCH = {
        "API":     "https://pro-api.coinmarketcap.com",
        "SANDBOX": "https://sandbox-api.coinmarketcap.com",
        "DEBUG":   os.path.join(os.getcwd(), "data"),
        "ARCHIVE": os.path.join(os.getcwd(), "data"),
    }

    def __init__(self, ticker: str, name: str, id: Iterable, coins: float, currency: str, endpoint: str, run_type="API"):
        super().__init__(ticker, name, id, coins, currency)

        run_type = run_type.upper()
        if run_type not in self.RUN_TYPE_OPTIONS:
            raise ValueError(f"Variable 'run_type' must be one of the values in {self.RUN_TYPE_OPTIONS}." +
                             f"'{run_type}' is not valid.")

        self.__run_type = run_type
        self.__endpoint = self.__config(endpoint=endpoint)
        self.request()

    @property
    def coins(self):
        return self._Investment__count

    @property
    def response(self):
        return self._Investment__response

    @property
    def url(self):
        # The Free Crypto API Call endpoint URL for the held cryptocurrency assets
        run_type      = self.__run_type
        endpoint_type = self.__endpoint['endpoint_type']
        domain        = self.URL_SWITCH.get(run_type)

        if self.__run_type.upper() in ["API", "SANDBOX"]:
            endpoint = self.__endpoint["endpoint_url"]
            return urllib.parse.urljoin(domain, endpoint)
        else:
            endpoint = f"debug_{self.ARCHIVE_FILES[endpoint_type]}"
            return os.path.join(domain, endpoint)

    def combine_responses(self, mode="w", suffix=""):
        possible_modes = ["w", "a"]
        if mode not in possible_modes:
            raise ValueError(f"Variable 'mode' must be one of the values in {possible_modes}." +
                             f"'{mode}' is not valid.")

        domain        = self.URL_SWITCH.get("ARCHIVE")
        endpoint_type = self.__endpoint['endpoint_type']
        endpoint      = self.ARCHIVE_FILES[endpoint_type]
        endpoint, _   = os.path.splitext(endpoint)
        suffix        = "" if not suffix else "_" + suffix
        endpoint      = 'archive_' + endpoint.replace('debug', '') + suffix + ".csv"        
        filename      = os.path.join(domain, endpoint)
        
        df_new = pd.json_normalize(self.response["data"])
        df_new.columns = ['.'.join(re.split("\.", col)[1:]) for col in df_new.columns]
        df_new = pd.DataFrame(
            {col: df_new.loc[:, col].stack(dropna=False).values for col in df_new.columns.unique()}
        )

        if mode == "w" or not os.path.isfile(filename):
            df_new.to_csv(filename)
            df_merged = df_new
        else:
            df_prev = pd.read_csv(filename)
            df_merged = pd.concat([df_prev, df_new], axis=0)
            df_merged.to_csv(filename)

        self.dataframe = df_merged

    def json_to_dataframe(self):
        # If defined, response will take precedence over self.response.
        if not self.response:
            return None

        df       = pd.DataFrame(self.response["data"])
        id       = self.id
        run_type = self.__run_type
        endpoint = self.__endpoint["endpoint_type"]     
        
        # Define function for dataframe formatting.
        df_switch_endpoint = {
            "info":            lambda x: x,
            "latest-listings": lambda x: x.loc[x["id"].map(str).isin(id), :] if run_type != "SANDBOX" else x,
            "latest-quotes":   lambda x: x.T.reset_index(),
        }

        # Return formatted dataframe      
        return df_switch_endpoint.get(endpoint)(df)

    def dataframe(self):
        return self.dataframe

    def request(self):
        # Using the Python requests library, make an API call to access the current
        # price of BTC

        print(f"Source   : {self.url}")
        print(f"RUN TYPE : {self.__run_type.upper()}")

        # Set request credentialsa and params
        headers = {
            "Accepts":           "application/json",
            "Accept-Encoding":   "deflate, gzip",
            "X-CMC_PRO_API_KEY": os.getenv("X-CMC_PRO_API_KEY"),
        }

        parameters = {
            "start":   "1",
            "limit":   self.coins,
            "convert": self.currency,
            "slug":    ",".join([n.lower() for n in self.name]),
            "id":      ",".join(self.id),
        }

        # Set url request
        session_get_switch = {
            "metadata":        lambda : session.get(self.url, params={k: parameters[k] for k in ["slug",]}),
            "latest-listings": lambda : session.get(self.url, params={k: parameters[k] for k in ["start", "limit", "convert"]}),
            "latest-quotes":   lambda : session.get(self.url, params={k: parameters[k] for k in ["id"]})
        }

        endpoint_type = self.__endpoint['endpoint_type']

        if self.__run_type.upper() in ["API", "SANDBOX"]:
            # Get CoinMarketCap Response
            session = Session()
            session.headers.update(headers)

            try:
                response = session_get_switch.get(endpoint_type)()
                self._Investment__response = json.loads(response.text)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)
        else:
            # Get Saved Data
            with open(self.url, "r", encoding="utf-8") as f:
                self._Investment__response = json.loads(f.read())
            
        self.dataframe = self.json_to_dataframe()

    def print_json_dump(self):
        print(json.dumps(self.response, indent=4, sort_keys=True))

    @staticmethod
    def __config(endpoint=None):

        outvars = {
            "endpoint_prefix": "v1/cryptocurrency/",        
        }

        endpoint_switch  = {
            "cmc-id":                  "map",
            "metadata":                "info",
            "latest-listings":         "listings/latest",
            "historical-listings":     "listings/historical",
            "latest-quotes":           "quotes/latest",
            "historical-quotes":       "quotes/historical",
            "latest-market-pairs":     "market-pairs/latest",
            "latest-ohlcv":            "ohlcv/latest",
            "historical-ohlcv":        "ohlcv/historical",
            "price-performance-stats": "price-performance-stats/latest",
        }

        def endpoint_error(var, switch):
            raise AssertionError(f"Using 'endpoint' of value '{var}' is not supported.\n"
                f"\tOnly: {list(switch.keys())}")

        if endpoint:
            if endpoint in endpoint_switch.keys():
                endpoint_suffix = endpoint_switch.get(endpoint)
                endpoint_url    = urllib.parse.urljoin(outvars["endpoint_prefix"], endpoint_suffix)
                outvars = {**outvars, **{"endpoint_url": endpoint_url, "endpoint_suffix": endpoint_suffix, "endpoint_type": endpoint}}
            else:
                endpoint_error(endpoint, endpoint_switch)

        return outvars

