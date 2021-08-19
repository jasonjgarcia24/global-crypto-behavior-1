
import pandas as pd 


def crypto_cleaner(df):
    # Filling NAs
    df["max_supply"] = df["max_supply"].fillna(0).astype(int)
    df["circulating_supply"]= df["circulating_supply"].fillna(0).astype(int)
    df["total_supply"]= df["total_supply"].fillna(0).astype(int)

    # Parsing columns
    df1 = df[['name', 'symbol','num_market_pairs',
        'last_updated', 'quote']]

    # Extracting data from Quote column
    df_quote = pd.DataFrame(df1["quote"])

    all = []
    for x in df_quote["quote"]:
        all.append(x["USD"])
    new_df = pd.DataFrame(all)

    # Manipulating and cleaning the combined data frame 
    df_combined = df1.join(new_df,rsuffix="_quote").drop(columns= ["last_updated_quote","quote"])
    df_combined["volume_24h"] = df_combined["volume_24h"].fillna(0).astype(int)
    df_combined["market_cap"] = df_combined["market_cap"].fillna(0).astype(int)
    df_combined["fully_diluted_market_cap"] = df_combined["fully_diluted_market_cap"].fillna(0).astype(int)
    df_combined["last_updated"]= pd.to_datetime( df_combined["last_updated"],infer_datetime_format=True)

    return df_combined

   