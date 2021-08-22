# Import the required libraries and dependencies
import os
import re
import urllib
import json

import pandas as pd

from dotenv   import load_dotenv
from requests import Session
from datetime import datetime
from pathlib  import Path

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
        "metadata":        "metadata_data.csv",
        "latest-listings": "latest-listing_data.csv",
        "latest-quotes":   "latest-quotes_data.csv",
    }

    RUN_TYPE_OPTIONS = ["API", "SANDBOX", "DEBUG"]
    SAVE_CSV_OPTIONS = [None, "a", "w"]

    DOMAIN_SWITCH = {
        "API":     "https://pro-api.coinmarketcap.com",
        "SANDBOX": "https://sandbox-api.coinmarketcap.com",
        "DEBUG":   os.path.join(os.getcwd(), "data"),
    }

    def __init__(self, ticker: str, name: str, id: Iterable, coins: float, currency: str, endpoint: str,
                 run_type="API", save_csv=None):
        super().__init__(ticker, name, id, coins, currency)

        self.__catch_value_error(run_type, "run_type", self.RUN_TYPE_OPTIONS)
        self.__catch_value_error(save_csv, "save_csv", self.SAVE_CSV_OPTIONS)

        self.__run_type = run_type
        self.save_csv   = save_csv
        self.__set_endpoint(endpoint)
        self.request()

    @property
    def coins(self):
        return self._Investment__count

    @property
    def url(self):
        # The Free Crypto API Call endpoint URL for the held cryptocurrency assets
        run_type     = self.__run_type
        endpoint_tag = self.__endpoint['endpoint_tag']
        domain       = self.DOMAIN_SWITCH.get(run_type)
        prefix       = run_type.lower()

        if run_type.upper() in ["API", "SANDBOX"]:
            endpoint = self.__endpoint["endpoint_url"]
            return urllib.parse.urljoin(domain, endpoint)
        else:
            endpoint = f"{prefix}_{self.ARCHIVE_FILES[endpoint_tag]}"
            return os.path.join(domain, endpoint)

    @property
    def response(self):
        return self._Investment__response

    def dataframe(self):
        if not self.__response:
            return None
        else:
            return self.dataframe

    def __set_endpoint(self, endpoint_tag):
        endpoint = {
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

        if endpoint_tag not in endpoint_switch.keys():
            raise AssertionError(f"Using 'endpoint' of value '{var}' is not supported.\n"
                f"\tOnly: {list(switch.keys())}")

        if endpoint_tag in endpoint_switch.keys():
            endpoint_suffix = endpoint_switch.get(endpoint_tag)
            endpoint_url    = urllib.parse.urljoin(endpoint["endpoint_prefix"], endpoint_suffix)
            endpoint        = {**endpoint, **{"endpoint_url":    endpoint_url,
                                                "endpoint_suffix": endpoint_suffix,
                                                "endpoint_tag":    endpoint_tag}}

        self.__endpoint = endpoint
        
    def request(self):
        # Using the Python requests library, make a CoinMarketCap API call to access the current
        # cryptocurrency statistics.

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

        endpoint_tag = self.__endpoint['endpoint_tag']

        # Get CoinMarketCap API response and data:
        if self.__run_type.upper() in ["API", "SANDBOX"]:
            session = Session()
            session.headers.update(headers)

            try:
                response = session_get_switch.get(endpoint_tag)()
                self._Investment__response = json.loads(response.text)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)

            self.dataframe = self.json_to_dataframe()
        
        # Get saved data:
        else:
            self.dataframe = pd.read_csv(Path(self.url))

        # Save dataframe to csv.
        if self.save_csv:
            self.to_csv(mode=self.save_csv, suffix="auto")

    def json_to_dataframe(self):
        if not self.response:
            return pd.DataFrame()

        df = pd.json_normalize(self.response["data"])

        # Remove CryptoMarketCap ID from column names.
        df.columns = ['.'.join(re.split("\.", col)[1:]) for col in df.columns]
        df = pd.DataFrame(
            {col: df.loc[:, col].stack(dropna=False).values for col in df.columns.unique()}
        )

        return df

    def merge_df_responses(self, filename):
        df_new    = self.dataframe
        df_prev   = pd.read_csv(filename)
        df_merged = pd.concat([df_prev, df_new], axis=0)

        return df_merged

    def print_json_dump(self):
        print(json.dumps(self.response, indent=4, sort_keys=True))

    def to_csv(self, mode="a", suffix=""):
        self.__catch_value_error(mode, "mode", [opt for opt in self.SAVE_CSV_OPTIONS if opt])

        # Set to data archive domain: os.path.join(os.getcwd(), "data")
        run_type = self.__run_type
        domain   = self.DOMAIN_SWITCH.get("DEBUG")

        # Archive (types: endpoints) can be:
        # "metadata":        "metadata_data.json",
        # "latest-listings": "latest-listing_data.json",
        # "latest-quotes":   "latest-quotes_data.json",
        endpoint_tag = self.__endpoint['endpoint_tag']
        endpoint     = self.ARCHIVE_FILES[endpoint_tag]

        # Modify endpoints to include suffix and date if mode == "w".
        today         = "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix        = run_type.lower() + "_" if run_type in ["SANDBOX", "DEBUG"] else ""
        endpoint, ext = os.path.splitext(endpoint)
        suffix        = "" if not suffix else "_" + suffix
        suffix        = suffix+today if mode=="w" else suffix
        endpoint      = prefix + endpoint + suffix + ext

        # Assign filename.
        filename = os.path.join(domain, endpoint)

        # If writing to file:
        # Write to file.
        if mode == "w" or not os.path.isfile(filename):
            self.dataframe.to_csv(filename, index=False)

        # If appending to file:
        # Read the existing file, concatenate with new data, and write to file.
        elif mode == "a":
            self.dataframe = self.merge_df_responses(filename)
            self.dataframe.to_csv(filename, index=False)

    @staticmethod
    def __catch_value_error(var, varname, opts):
        if var not in opts:
            raise ValueError(f"Variable '{varname}' must be one of the values in {opts}." +
                             f"'{var}' is not valid.")

