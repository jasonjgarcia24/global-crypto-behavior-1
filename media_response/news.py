import os
import json

from dotenv   import load_dotenv
from requests import Session

from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


class CryptoNewsResponse():
    URL_SWITCH = {
        "API":     "https://cryptonews-api.com/api/v1",
        "DEBUG":   os.path.join(os.getcwd(), "data"),
        "ARCHIVE": os.path.join(os.getcwd(), "data"),
    }

    def __init__(self, ticker: str, items=2, endpoint="", rank_days=1, run_type="API"):
        self.ticker    = ticker
        self.items     = items
        self.endpoint  = endpoint
        self.rank_days = rank_days
        self.run_type  = run_type
        self.request()

    @property
    def url(self):
        return self.URL_SWITCH["API"]

    def request(self):
        load_dotenv()        

        # Set request credentialsa and params  
        crypto_news_api_key = os.getenv("CRYPTO_NEWS_API_KEY")

        parameters = {
            "tickers":      ",".join(self.ticker),
            "items":        self.items,
            "sortby":       "rank",
            "days":         self.rank_days,
            "extra-fields": "id,eventid,rankscore",
            "token":   crypto_news_api_key,
        }

        session = Session()

        try:
            response = session.get(self.url, params=parameters)
            self.__response = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        breakpoint()

    def print_json_dump(self):
        print(json.dumps(self.__response, indent=4, sort_keys=True))

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
    def get_news_source_opts(): return list(CryptoNewsResponse.config()["news-source"].keys())

    @staticmethod
    def get_type_opts(): return list(CryptoNewsResponse.config()["type"].keys())

    @staticmethod
    def get_sentiment_bias_opts(): return list(CryptoNewsResponse.config()["sentiment-bias"].keys())

    @staticmethod
    def get_rank_opts(): return list(CryptoNewsResponse.config()["rank"].keys())

    @staticmethod
    def get_extra_fields_opts(): return list(CryptoNewsResponse.config()["extra-fields"].keys())

    @staticmethod
    def get_all_ticker_news_opts(): return list(CryptoNewsResponse.config()["all-ticker-news"].keys())

    @staticmethod
    def get_sentiment_analysis_opts(): return list(CryptoNewsResponse.config()["sentiment-analysis"].keys())

    @staticmethod
    def get_time_frame_opts(): return list(CryptoNewsResponse.config()["time-frame"].keys())

    @staticmethod
    def get_topic_opts(): return list(CryptoNewsResponse.config()["topics"].keys())
