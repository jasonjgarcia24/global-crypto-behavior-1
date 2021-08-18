import pandas as pd

def data_pull(date_var):
    data_crypto_news = pd.read_csv(f"./data/ticker-news_data_{date_var}.csv")
    data_crypto_news["date"]= pd.to_datetime( data_crypto_news["date"],infer_datetime_format=True)
    data_crypto_news.drop_duplicates()
    data_crypto_news= data_crypto_news.drop(columns= ['image_url','type','news_id','eventid'])
    return data_crypto_news

Crypto_news_df = data_pull("20210815")
Crypto_news_df