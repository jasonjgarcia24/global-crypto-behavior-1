import pandas as pd

from dateutil import tz


def set_et_timestamp(client_timestamp):
    et_zone = tz.gettz('America/New_York')

    return client_timestamp.astimezone(et_zone)


def get_et_datetime(client_timestamp, strformat):
    # Find the set timezone and convert to "America/New_York" (ET).
    et_timestamp = set_et_timestamp(client_timestamp)
    
    return et_timestamp.strftime(strformat)


def get_et_pd_timestamp(client_timestamp):
    et_timestamp = set_et_timestamp(client_timestamp)    

    return pd.Timestamp(et_timestamp)