import sys
sys.path.append('.')

import pandas as pd


def date_str_func(suffix):
    return f"./data/latest-quotes_data_{suffix}.csv"


def data_pull(date_var):
    data_crypto = pd.read_csv(date_str_func(date_var))
    
    data_crypto["max_supply"] = data_crypto["max_supply"].fillna(0).astype(int)
    data_crypto["circulating_supply"]= data_crypto["circulating_supply"].fillna(0).astype(int)
    data_crypto["total_supply"]= data_crypto["total_supply"].fillna(0).astype(int)
    data_crypto["quote.USD.market_cap"]= data_crypto["quote.USD.market_cap"].fillna(0).astype(int)
    data_crypto["quote.USD.fully_diluted_market_cap"]= data_crypto["quote.USD.fully_diluted_market_cap"].fillna(0).astype(int)
    data_crypto["date_added"]= pd.to_datetime( data_crypto["date_added"],infer_datetime_format=True, utc=True)
    data_crypto["quote.USD.last_updated"] = pd.to_datetime( data_crypto["quote.USD.last_updated"],infer_datetime_format=True, utc=True)
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
                            'date_added'])
    return data_crypto_df


def write_df(df, date_var):
    df.to_csv(date_str_func(date_var), mode="w")


if __name__ == "__main__":
    for d in [20]:
        date_var  = f"202108{d}"
        crypto_df = data_pull(date_var)

        write_df(crypto_df, date_var)

