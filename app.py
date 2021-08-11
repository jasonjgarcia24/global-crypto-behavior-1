from market_response.crypto import CoinMarketCapResponse

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
endpoint       = "listings/latest"

data = CoinMarketCapResponse(tickers, slugs,  coins, currency, endpoint,
                             make_request=True, debug="YES")

breakpoint()
