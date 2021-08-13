# Import the required libraries and dependencies
import os
import urllib
import requests
import json
import functools

import pandas as pd

from requests import Request, Session
from datetime import datetime
from dotenv   import load_dotenv
from requests import Request, Session

from collections.abc     import Iterable
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects, ValueError
from utils.timezone      import get_et_datetime, get_et_pd_timestamp


class Investment:
    load_dotenv()

    YEARLY_TRADING_DAYS = 252
    INVESTMENT_TYPES = {
        "FreeCryptoResponse": "crypto",
        "AlpacaBarset": "shares"
    }
    INVESTMENT_TYPES_STR = "|".join(INVESTMENT_TYPES.keys())

    def __init__(self, ticker: str, name: str, id: Iterable, count: float,
                 currency: str, portfolio: str, time_format: str):
        self.ticker      = ticker
        self.name        = name
        self.id          = id
        self.__count     = count
        self.currency    = currency
        self.portfolio   = portfolio
        self.time_format = time_format
        self.__response  = None

    @property
    def title(self):
        return f"{self.name} ({self.ticker})"

    def closing_price_print(self):
        # A function to print a the closing price of an investment
        if self.price:
            print(f"As of {self.collection_time},\n"
                  f"the closing price of the {self.portfolio}'s\n"
                  f"{self.title} is {self.price:,.2f} USD.")
        else:
            print(f"A {self.INVESTMENT_TYPES_STR} response is required for a price. No price set.")

    def closing_value_print(self):
        # A function to print a the closing value of an investment
        if self.value:
            print(f"As of {self.collection_time},\n"
                  f"the total value of the {self.portfolio}'s\n"
                  f"{self.__count:.1f} {self.title} is {self.value:,.2f} USD.")
        else:
            print(f"A {self.INVESTMENT_TYPES_STR} response is required for a value. No value set.")

    def __validate_investment_list(func):
        # A validator for verifying input argument type is list, tuple, or set of
        # FreeCryptoResponse and/or AlpacaBarset objects
        def checktype(var, varname=''):
            # Check if var is a list, tuple, or set
            is_lts = isinstance(var, list) or isinstance(var, tuple) or isinstance(var, set)

            if not is_lts:
                raise TypeError(f"Variable {varname} '{type(var)}' object is not list, tuple, nor set.")

            return is_lts

        @functools.wraps(func)
        def wrapper_validator(*args, **kwargs):
            investment_varname = "investments"
            investment_types = Investment.INVESTMENT_TYPES.keys()
            investment_str = '|'.join([_type for _type in investment_types])
            investment_arg = kwargs[investment_varname] if investment_varname in kwargs else args[-1]

            # If not list, tuple, or set, this call will resort in a TypeError and no call
            # to func()
            checktype(investment_arg, varname=investment_varname)

            # Check if FreeCryptoResponse and/or AlpacaBarset objects are used
            for inv in investment_arg:
                if not type(inv).__name__ in investment_types:
                    raise AssertionError(f"Using {investment_varname} of type '{type(inv).__name__}' is not supported\n"
                                         f"({investment_str} only)")
            return func(*args, **kwargs)

        return wrapper_validator

    @staticmethod
    def combine_investments_title_str(investment, precision=2):
        # A function used internally by create_investment_dict() for parsing
        # FreeCryptoResponse or AlpacaBarset objects for necessary information
        # This is te parsing function
        investment_strs = [" ".join([f"{val['count']:.{precision}f}", key])
                           for key, val in investment.items()]
        investment_strs = " and ".join(investment_strs)

        return investment_strs

    @classmethod
    def create_investment_dict(cls, investments):
        # A function used internally by closing_portfolio_balance_print() and
        # ci_portfolio_print() to parse a list of FreeCryptoResponse and/or AlpacaBarset
        # objects for necessary information
        # This is the merging function
        investments_dict = {val: {} for val in cls.INVESTMENT_TYPES.values()}

        if investments:
            if not isinstance(investments, list): investments = [investments, ]

            for inv in investments:
                inv_class = type(inv).__name__
                inv_type = cls.INVESTMENT_TYPES.get(inv_class)
                inv_dict = {inv.title: {"count": inv.__count, "class": inv_class}}

                investments_dict[inv_type] = {**investments_dict[inv_type], **inv_dict}

        return investments_dict

    @classmethod
    def get_investment_strs(cls, coins=None, shares=None):
        # A function to organize crypto and share investments in a single concatenated string
        share_strs = ""
        coin_strs = ""
        if shares:
            share_strs += cls.combine_investments_title_str(shares, precision=1) + " shares"

        if coins:
            coin_strs += cls.combine_investments_title_str(coins, precision=2) + " coins"

        share_strs = ", \nand ".join(filter(None, [share_strs, coin_strs]))

        return share_strs

    @classmethod
    @__validate_investment_list
    def closing_portfolio_balance_print(cls, portfolio, investments=list()):
        # A function to print a portfolio of multiple investments
        if not all([True if inv.value else False for inv in investments]):
            print(f"A {cls.INVESTMENT_TYPES_STR} response for all investments is required for a value. No value set.")
            return

        collection_time = max([inv.collection_time for inv in investments])
        total_value = sum(inv.value for inv in investments)

        investments_dict = cls.create_investment_dict(investments)
        investment_strs = cls.get_investment_strs(coins=investments_dict["crypto"],
                                                  shares=investments_dict["shares"])

        print(f"As of {collection_time},\n"
              f"the total closing value of the {portfolio} containing\n"
              f"{investment_strs}\n"
              f"is {total_value:,.2f} USD.")

    @classmethod
    @__validate_investment_list
    def ci_portfolio_print(cls, pct: str, portfolio: str, conf_idx: list, investments=list()):
        # A function to print projected confidence indexes with projected portfolio returns
        if not all([True if inv.value else False for inv in investments]):
            print(f"A {cls.INVESTMENT_TYPES_STR} response for all investments is required for a value. No value set.")
            return

        investments_dict = cls.create_investment_dict(investments)
        share_strs = cls.get_investment_strs(coins=investments_dict["crypto"],
                                             shares=investments_dict["shares"])

        total_value = sum(inv.value for inv in investments)
        percent_change = [(ci - total_value) / total_value * 100 for ci in conf_idx]

        print(f"The lower and upper {int(pct)}% confidence intervals\n"
              f"of the {portfolio} containing\n"
              f"{share_strs}\n"
              f"are {conf_idx[0]:,.2f} USD ({percent_change[0]:,.2f}%) and {conf_idx[1]:,.2f} USD ({percent_change[1]:,.2f}%).")


class CoinMarketCapResponse(Investment):
    DEBUG_FILE = {
            "metadata":        "debug_metadata_data.json",
            "latest-listings": "debug_latest-listing_data.json",
            "latest-quotes":   "debug_latest-quotes_data.json",
    }

    RUN_TYPE_OPTIONS = ["API", "DEBUG", "SANDBOX"]
        
    URL_SWITCH = {
        "API":      "https://pro-api.coinmarketcap.com",
        "DEBUG":     os.path.join(os.getcwd(), "data"),
        "SANDBOX": "https://sandbox-api.coinmarketcap.com",
    }

    def __init__(self, ticker: str, name: str, id: Iterable, coins: float, currency: str, endpoint: str,
                 save_response="NO", run_type="API"):
        super().__init__(ticker, name, id, coins, currency, "cryptocurrency wallet", "%a, %Y-%b-%d %H:%M:%S (%Z)")

        if run_type not in RUN_TYPE_OPTIONS:
            raise ValueError(f"Variable 'run_type' must be one of the values in {RUN_TYPE_OPTIONS}. '{run_type}' is not valid.")

        self.__run_type      = run_type
        self.__endpoint      = self.__config(endpoint=endpoint)
        self.__save_response = save_response
        self.request()

    @property
    def coins(self):
        return self._Investment__count

    @property
    def response(self):
        return self._Investment__response

    @property
    def collection_time(self):
        # Navigate the crypto response object to access the datetime string of crypto
        if not self.response:
            return None

        timestamp = datetime.fromtimestamp(self.response["metadata"]["timestamp"])
        return get_et_datetime(timestamp, self.time_format)

    @property
    def collection_timestamp(self):
        # Navigate the crypto response object to access the timestamp of crypto
        if not self.response:
            return None

        timestamp = datetime.fromtimestamp(self.response["metadata"]["timestamp"])
        return get_et_pd_timestamp(timestamp)

    @property
    def price(self):
        # Navigate the crypto response object to access the current price of crypto
        if not self.response:
            return None

        return float(self.response["data"][self.id]["quotes"]["USD"]["price"])

    @property
    def value(self):
        # Compute the current value of the crypto holding
        if not self.response:
            return None

        return self.coins * self.price

    @property
    def url(self):
        # The Free Crypto API Call endpoint URL for the held cryptocurrency assets
        debug_type = self.debug.upper()
        domain     = self.URL_SWITCH.get(debug_type)

        if debug_type == "DEBUG":
            endpoint = f"debug_{self.__endpoint['endpoint_type']}_data.json"
            return os.path.join(domain, endpoint)
        else:
            endpoint = self.__endpoint["endpoint_url"]
            return urllib.parse.urljoin(domain, endpoint)

    def __set_dataframe(self):
        if not self.response:
            return None

        df = pd.DataFrame(self.response["data"])
        
        df_switch_endpoint = {
            "info":            lambda x: x,
            "latest-listings": lambda x: x.loc[x["id"].map(str).isin(self.id), :] if self.__run_type != "SANDBOX" else x,
            "latest-quotes":   lambda x: x.T.reset_index(),
        }

        endpoint_type  = self.__endpoint["endpoint_type"]
        self.dataframe = df_switch_endpoint.get(endpoint_type)(df)

    def __save_json(self):
        breakpoint()
        gh = 1

        fn      = f"debug_{catch_endpoint_type}_data.json"
        full_fn = os.path.join(self.URL_SWITCH.get("DEBUG"), fn)

    def dataframe(self):
        return self.dataframe

    def request(self):
        # Using the Python requests library, make an API call to access the current
        # price of BTC

        print(f"Source   : {self.url}")
        print(f"RUN TYPE : {self.__run_type.upper()}")
        print(f"SAVE     : {self.__save_response.upper()}\n")

        # Set read params and credentials
        parameters = {
            "start":   "1",
            "limit":   self.coins,
            "convert": self.currency,
            "slug":    ",".join([n.lower() for n in self.name]),
            "id":      ",".join(self.id),
        }

        headers = {
            "Accepts":           "application/json",
            "Accept-Encoding":   "deflate, gzip",
            "X-CMC_PRO_API_KEY": os.getenv("X-CMC_PRO_API_KEY"),
        }

        # Set url request
        session_get_switch = {
            "metadata":        lambda : session.get(self.url, params={k: parameters[k] for k in ["slug",]}),
            "latest-listings": lambda : session.get(self.url, params={k: parameters[k] for k in ["start", "limit", "convert"]}),
            "latest-quotes":   lambda : session.get(self.url, params={k: parameters[k] for k in ["id"]})
        }

        catch_endpoint_type = self.__endpoint["endpoint_type"]

        if self.__run_type.upper() in ["API", "SANDBOX"]:
            # Get CoinMarketCap Response
            session = Session()
            session.headers.update(headers)

            try:
                breakpoint()
                response = session_get_switch.get(catch_endpoint_type)()
                self._Investment__response = json.loads(response.text)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)
        else:
            # Get Saved Data
            fn      = f"debug_{catch_endpoint_type}_data.json"
            full_fn = os.path.join(self.URL_SWITCH.get("DEBUG"), fn)

            with open(full_fn, "r", encoding="utf-8") as f:
                self._Investment__response = json.loads(f.read())
            
        self.__set_dataframe()
        self.__save_json()

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

        