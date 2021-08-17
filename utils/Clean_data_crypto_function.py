import pandas as pd

def data_pull(date_var):
    data_crypto = pd.read_csv(f"./data/latest-quotes_data_{date_var}.csv")
    data_crypto["max_supply"] = data_crypto["max_supply"].fillna(0).astype(int)
    data_crypto["circulating_supply"]= data_crypto["circulating_supply"].fillna(0).astype(int)
    data_crypto["total_supply"]= data_crypto["total_supply"].fillna(0).astype(int)
    data_crypto["quote.USD.market_cap"]= data_crypto["quote.USD.market_cap"].fillna(0).astype(int)
    data_crypto["quote.USD.fully_diluted_market_cap"]= data_crypto["quote.USD.fully_diluted_market_cap"].fillna(0).astype(int)
    data_crypto["date_added"]= pd.to_datetime( data_crypto["date_added"],infer_datetime_format=True)
    data_crypto["quote.USD.last_updated"] = pd.to_datetime( data_crypto["quote.USD.last_updated"],infer_datetime_format=True)
    data_crypto_df = data_crypto.drop(columns = ["id", 
                            "tags", 
                            'max_supply',
                            'circulating_supply',
                            'total_supply',
                            'quote.USD.market_cap', 
                            'quote.USD.market_cap_dominance',
                            'quote.USD.fully_diluted_market_cap',
                            'is_fiat',
                            'platform',
                            'quote.USD.volume_24h',
                            'quote.USD.price',
                            'date_added'])
    return data_crypto_df


crypto_df = data_pull("20210814")
crypto_df