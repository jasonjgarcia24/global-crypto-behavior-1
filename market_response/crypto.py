# Import the required libraries and dependencies
import os
import requests
import json
import functools

import pandas as pd

from requests import Request, Session
from datetime import datetime
from dotenv   import load_dotenv
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from utils.timezone import get_et_datetime, get_et_pd_timestamp


class Investment:
    load_dotenv()

    YEARLY_TRADING_DAYS = 252
    INVESTMENT_TYPES = {
        "FreeCryptoResponse": "crypto",
        "AlpacaBarset": "shares"
    }
    INVESTMENT_TYPES_STR = "|".join(INVESTMENT_TYPES.keys())

    def __init__(self, ticker: str, name: str, count: float,
                 currency: str, portfolio: str, time_format: str,
                 debug="NO"):
        self.ticker      = ticker
        self.name        = name
        self.__count     = count
        self.currency    = currency
        self.portfolio   = portfolio
        self.time_format = time_format
        self.__response  = None
        self.__debug     = debug

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
    QUERY = "/v1/cryptocurrency"
        
    URL_SWITCH = {
        "NO":      f"https://pro-api.coinmarketcap.com{QUERY}",
        "YES":     r"C:\Users\JasonGarcia24\FINTECH-WORKSPACE\global-crypto-behavior\data\debug_data.json",
        "SANDBOX": f"https://sandbox-api.coinmarketcap.com{QUERY}",
    }

    def __init__(self, ticker: str, name: str, coins: float, currency: str, endpoint: str,
                 make_request=False, debug="NO"):
        super().__init__(ticker, name, coins, currency,
                         "cryptocurrency wallet", "%a, %Y-%b-%d %H:%M:%S (%Z)",
                         debug)

        self.endpoint = endpoint

        if make_request:
            self.request()

    @property
    def coins(self):
        return self._Investment__count

    @property
    def response(self):
        return self._Investment__response

    @property
    def id(self):
        # Navigate the crypto response object to access the id of crypto
        if not self.response:
            return None

        return list(self.response["data"].keys())[0]

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
        return f"{self.URL_SWITCH.get(self.debug.upper())}/{self.endpoint}"

    @property
    def debug(self):
        return self._Investment__debug

    def __set_dataframe(self):
        if not self.response:
            return None

        df = pd.DataFrame(self.response["data"])
        breakpoint()
        
        self.dataframe = df.loc[df["name"].isin(self.name), :]

    def dataframe(self):
        return self.dataframe

    def request(self):
        # Using the Python requests library, make an API call to access the current
        # price of BTC

        if self.debug.upper() in ["NO", "SANDBOX"]:
            parameters = {
                "start":   "1",
                "limit":   self.coins,
                "convert": self.currency,
                # "slug":    ",".join([n.lower() for n in self.name])
            }

            headers = {
                "Accepts": "application/json",
                "Accept-Encoding": "deflate, gzip",
                "X-CMC_PRO_API_KEY": os.getenv("X-CMC_PRO_API_KEY"),
            }

            session = Session()
            session.headers.update(headers)
            # response = session.get(url, params=parameters)

            session_get_switch = {
                "listings/latest": lambda : session.get(self.url, params={k: parameters[k] for k in ["start", "limit", "convert"]}),
                "info":            lambda : session.get(self.url, params={k: parameters[k] for k in ["slug",]})
            }

            try:
                breakpoint()
                response = session_get_switch.get(self.endpoint)()
                self._Investment__response = json.loads(response.text)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)
        else:
            with open(self.URL_SWITCH.get("YES"), "r", encoding="utf-8") as f:
                self._Investment__response = json.loads(f.read())
            
        self.__set_dataframe()

    def print_json_dump(self):
        print(json.dumps(self.response, indent=4, sort_keys=True))
