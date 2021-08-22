import sys
sys.path.append('.')

import pandas as pd


def date_str_func(suffix):
    return f"./data/ticker-news_data_{suffix}.csv"


def data_pull(date_var):
    filename         = date_str_func(date_var)
    data_crypto_news = pd.read_csv(filename)
    data_crypto_news = data_crypto_news[data_crypto_news["tickers"].notna()]

    data_crypto_news["date"] = pd.to_datetime(data_crypto_news["date"],infer_datetime_format=True, utc=True)
    data_crypto_news = data_crypto_news.drop_duplicates()
    data_crypto_news = data_crypto_news.drop(columns= ['type','news_id','eventid'])

    return data_crypto_news


def write_df(df, date_var):
    df.to_csv(date_str_func(date_var), mode="w")


if __name__ == "__main__":
    for d in range(14, 22):
        date_var       = f"202108{d}"
        crypto_news_df = data_pull(date_var)

        write_df(crypto_news_df, date_var)
    
