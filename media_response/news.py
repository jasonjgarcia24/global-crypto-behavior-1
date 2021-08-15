import os
import json

import pandas as pd

from dotenv   import load_dotenv
from requests import Session
from datetime import datetime
from pathlib  import Path

from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


class CryptoNewsResponse():
    ARCHIVE_FILES = {
        "ticker-news":   "ticker-news_data.csv",
        "ticker-events": "ticker-events_data.csv",
    }

    RUN_TYPE_OPTIONS = ["TICKER-NEWS", "TICKER-EVENTS", "DEBUG"]
    SAVE_CSV_OPTIONS = [None, "a", "w"]

    DOMAIN_SWITCH = {
        "TICKER-NEWS":   "https://cryptonews-api.com/api/v1",
        "TICKER-EVENTS": "https://cryptonews-api.com/api/v1/events",
        "DEBUG":         os.path.join(os.getcwd(), "data"),
    }

    def __init__(self, ticker: str, endpoint: str, items=2, rank_days=1,
                 run_type="TICKER-EVENTS", save_csv=None):

        self.__catch_value_error(run_type, "run_type", self.RUN_TYPE_OPTIONS)
        self.__catch_value_error(save_csv, "save_csv", self.SAVE_CSV_OPTIONS)

        self.ticker     = ticker
        self.items      = items
        self.rank_days  = rank_days
        self.__run_type = run_type
        self.save_csv   = save_csv
        self.__set_endpoint(endpoint)
        self.request()

    @property
    def url(self):
        run_type     = self.__run_type
        endpoint_tag = self.__endpoint
        domain       = self.DOMAIN_SWITCH.get(run_type)
        prefix       = run_type.lower()

        run_type = self.__run_type
        if run_type.upper() in ["TICKER-NEWS", "TICKER-EVENTS"]:
            return domain
        else:
            endpoint = f"{prefix}_{self.ARCHIVE_FILES[endpoint_tag]}"
            return os.path.join(domain, endpoint)

    @property
    def response(self):
        return self.__response

    def dataframe(self):
        if not self.__response:
            return None
        else:
            return self.dataframe

    def __set_endpoint(self, endpoint_tag):
        self.__endpoint = endpoint_tag
    
    def request(self):
        # Using the Python requests library, make an API call to access Crypto News
        # information.

        print(f"Source   : {self.url}")
        print(f"RUN TYPE : {self.__run_type.upper()}")

        # Set request credentialsa and params
        load_dotenv()
        crypto_news_api_key = os.getenv("CRYPTO_NEWS_API_KEY")

        parameters = {
            "tickers":      self.ticker if isinstance(self.ticker, str) else ",".join(self.ticker),
            "items":        self.items,
            "sortby":       "rank",
            "days":         self.rank_days,
            "extra-fields": "id,eventid,rankscore",
            "token":   crypto_news_api_key,
        }

        # Get CryptoNews Response:
        if self.__run_type.upper() in ["TICKER-NEWS", "TICKER-EVENTS"]:
            session = Session()

            try:
                response = session.get(self.url, params=parameters)
                self.__response = json.loads(response.text)
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
            return None
        else:        
            return pd.DataFrame(self.response["data"])

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
        # "ticker-news":   "ticker-news_data.csv",
        # "ticker-events": "ticker-events_data.csv",
        endpoint_tag = self.__endpoint
        endpoint     = self.ARCHIVE_FILES[endpoint_tag]

        # Modify endpoints to include suffix and date if mode == "w".
        today         = "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix        = run_type.lower() + "_" if run_type == "DEBUG" else ""
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

    @staticmethod
    def config():
        outargs = {}
        span_func     = lambda s, e: s + "-" + e
        multiple_func = lambda x: ",".join(x)

        outargs["news-source"] = {
            "altcoin-buzz":           ("Altcoin+Buzz",                  "Altcoin Buzz"),
            "ambcrypto":              ("AMBCrypto",                     "AMBCrypto"),
            "beincrypto":             ("BeInCrypto",                    "BeInCrypto"),
            "benzinga":               ("Benzinga",                      "Benzinga"),
            "bitcoin-com":            ("Bitcoin",                       "Bitcoin.com"),
            "bitcoin-market-journal": ("Bitcoin+Market+Journal",        "Bitcoin Market Journal"),
            "bitcoin-magazine":       ("Bitcoin+Magazine",              "Bitcoin Magazine"),
            "bitcoinist":             ("Bitcoinist",                    "Bitcoinist"),
            "bit-news":               ("Bit+News",                      "Bit News"),
            "blockgeeks":             ("Blockgeeks",                    "Blockgeeks"),
            "blockonomi":             ("Blockonomi",                    "Blockonomi"),
            "bloomberg-markets":      ("Bloomberg+Markets+and+Finance", "Bloomberg Markets and Finance (video)"),
            "bloomberg-tech":         ("Bloomberg+Technology",          "Bloomberg Technology (video)"),
            "btc-manager":            ("BTCManager",                    "BTC Manager"),
            "cnbc":                   ("CNBC",                          "CNBC (video)"),
            "cnbc-television":        ("CNBC+Television",               "CNBC Television (video)"),
            "cnn":                    ("CNN",                           "CNN (video)"),
            "coindesk":               ("Coindesk",                      "Coindesk"),
            "coindoo":                ("Coindoo",                       "Coindoo"),
            "coinfomania":            ("Coinfomania",                   "Coinfomania"),
            "coingape":               ("Coingape",                      "Coingape"),
            "coin-idol":              ("Coin+Idol",                     "Coin Idol"),
            "coinmarketcap":          ("CoinMarketCap",                 "CoinMarketCap"),
            "coin-news-asia":         ("Coin+News+Asia",                "Coin News Asia"),
            "coinnounce":             ("Coinnounce",                    "Coinnounce"),
            "crypto-briefing":        ("Crypto+Briefing",               "Crypto Briefing"),
            "crypto-daily":           ("Crypto+Daily",                  "Crypto Daily"),
            "crypto-economy":         ("Crypto+Economy",                "Crypto Economy"),
            "cryptonews":             ("CryptoNews",                    "CryptoNews"),
            "cryptoninjas":           ("CryptoNinjas",                  "CryptoNinjas"),
            "cryptopolitan":          ("Cryptopolitan",                 "Cryptopolitan"),
            "cryptopotato":           ("CryptoPotato",                  "CryptoPotato"),
            "crypto-reporter":        ("Crypto+Reporter",               "Crypto Reporter"),
            "cryptoslate":            ("CryptoSlate",                   "CryptoSlate"),
            "cryptoticker":           ("CryptoTicker",                  "CryptoTicker"),
            "cryptoverze":            ("Cryptoverze",                   "Cryptoverze"),
            "daily-fx":               ("DailyFX",                       "Daily FX"),
            "dc-forecasts":           ("DCForecasts",                   "DC Forecasts"),
            "decrypt":                ("Decrypt",                       "Decrypt"),
            "financemagnates":        ("FinanceMagnates",               "FinanceMagnates"),
            "forbes":                 ("Forbes",                        "Forbes"),
            "fox-business":           ("Fox+Business",                  "Fox Business"),
            "investorplace":          ("Investorplace",                 "Investorplace"),
            "koinpost":               ("Koinpost",                      "Koinpost"),
            "modern-consensus":       ("Modern+Consensus",              "Modern Consensus"),
            "newsbtc":                ("NewsBTC",                       "NewsBTC"),
            "reuters":                ("Reuters",                       "Reuters"),
            "the-block":              ("The+Block",                     "The Block"),
            "the-crypto-updates":     ("TCU",                           "The Crypto Updates"),
            "the-cryptonomist":       ("The+Cryptonomist",              "The Cryptonomist"),
            "the-currency-analytics": ("The+Currency+Analytics",        "The Currency Analytics"),
            "the-daily-hodl":         ("The+Daily+Hodl",                "The Daily Hodl"),
            "trustnode":              ("Trustnodes",                    "Trustnode"),
            "utoday":                 ("UToday",                        "UToday"),
            "yahoo-finance":          ("Yahoo+Finance",                 "Yahoo Finance"),
            "8btc":                   ("8BTC",                           "8BTC"),
        }

        outargs["type"] = {
            "video":   ("video", "Video"),
            "article": ("article", "Article"),
        }

        outargs["sentiment-bias"] = {
            "positive": ("positive", "Positive sentiment"),
            "negative": ("negative", "Negative sentiment"),
            "neutral":  ("neutral",  "Neutral sentiment"),
        }

        outargs["rank"] = {
            "rank":      ("rank", "Sort by rank"),
            "rank-days": ("rank&days", "Sort by rank for the last X days"),
            "oldest":    ("oldestfirst", "Sort by oldest first"),
        }

        outargs["extra-fields"] = {
            "news-id":    ("id",          "News ID"),
            "event-id":   ("eventid",     "Event ID"),
            "rank-score": ("rankscore",   "Rank score"),
            "multiple":   (multiple_func, "Combined"),
        }

        outargs["all-ticker-news"] = {
            "all": ("alltickers", "News published under all crypto tickers"),
        }

        outargs["sentiment-analysis"] = {
            "all":     ("alltickers", "All tickers and symbols"),
            "general": ("general",    "General crypto news"),
        }

        outargs["time-frame"] = {
            "-5m":         ("last5min",  "Last five minutes"),
            "-10m":        ("last10min", "Last ten minutes"),
            "-15m":        ("last15min", "Last fifteen minutes"),
            "-30m":        ("last30min", "Last thirty minutes"),
            "-45m":        ("last45min", "Last forty-five minutes"),
            "-60m":        ("last60min", "Last sixty minutes"),
            "0d":          ("today",     "Today"),
            "-1d":         ("yesterday", "Yesterday"),
            "-7d":         ("last7days", "Last seven days"),
            "-30d":        ("last30days", "Last thirty days"),
            "-60d":        ("last60days", "Last sixty days"),
            "-90d":        ("last90days", "Last ninety days"),
            "this-year":   ("yeartodate", "This year"),
            "format-date": ("%m%d%Y",     "Exact date"),
            "format-time": ("%H%M%S",     "Exact time"),
            "span"       : (span_func,    "Time span"),
        }

        outargs["topics"] = {
            "fb-diem-coin":   ("Diem",           "News related to Facebook's Diem coin"),
            "digital-dollar": ("Digital+Dollar", "News related to the Digital Dollar"),
            "digital-euro":   ("Digital+Euro",   "News related to the Digital Euro"),
            "digital-ruble":  ("Digital+Ruble",  "News related to the Digital Ruble"),
            "digital-yuan":   ("Digital+Yuan",   "News related to the Digital Yuan"),
            "futures":        ("Futures",        "News related to Futures contracts"),
            "libra":          ("Libra",          "News related to Facebook's Libra coin"),
            "mining":         ("Mining",         "News related to mining crypto"),
            "nft":            ("NFT",            "News related to NFT's"),
            "stablecoins":    ("Stablecoins",    "News related to Stablecoins"),
            "tech-analysis":  ("Tanalysis",      "News related to Technical Analysiss"),
            "taxes":          ("Taxes",          "News related to IRS and Taxes"),
            "upgrade":        ("Upgrade",        "News related to Upgrades and Hard Forks"),
            "whales":         ("Whales",         "News related to Whales Buying and Selling"),
            "multiple":       (multiple_func,    "Combined")
        }

        return outargs

    @staticmethod
    def get_news_source_opts():
        return list(CryptoNewsResponse.config()["news-source"].keys())

    @staticmethod
    def get_type_opts():
        return list(CryptoNewsResponse.config()["type"].keys())

    @staticmethod
    def get_sentiment_bias_opts():
        return list(CryptoNewsResponse.config()["sentiment-bias"].keys())

    @staticmethod
    def get_rank_opts():
        return list(CryptoNewsResponse.config()["rank"].keys())

    @staticmethod
    def get_extra_fields_opts():
        return list(CryptoNewsResponse.config()["extra-fields"].keys())

    @staticmethod
    def get_all_ticker_news_opts():
        return list(CryptoNewsResponse.config()["all-ticker-news"].keys())

    @staticmethod
    def get_sentiment_analysis_opts():
        return list(CryptoNewsResponse.config()["sentiment-analysis"].keys())

    @staticmethod
    def get_time_frame_opts():
        return list(CryptoNewsResponse.config()["time-frame"].keys())

    @staticmethod
    def get_topic_opts():
        return list(CryptoNewsResponse.config()["topics"].keys())
