import numpy  as np
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path


def stats_bar(df):
    df["sentiment_score"].name = "this_sentiment_score"

    df.columns = [str(col.lower()).replace(" ", "_") for col in df.columns]
    df[      "mentions"] = df.loc[:, [      "positive",       "negative",       "neutral"]].sum(axis=1)
    df["total_mentions"] = df.loc[:, ["total_positive", "total_negative", "total_neutral"]].sum(axis=1)

    df = df.sort_values(["ticker", "date"], ascending=True)
    customdata, hovertemplate = get_custom_data(df)

    fig = go.Figure([
        create_bar_trace(df["total_positive"], df["ticker"], "Positive Mentions", customdata=customdata, hovertemplate=hovertemplate),
        create_bar_trace(df["total_negative"], df["ticker"], "Negative Mentions", customdata=customdata, hovertemplate=hovertemplate),
        create_bar_trace(df["total_neutral"],  df["ticker"], "Neutral Mentions",  customdata=customdata, hovertemplate=hovertemplate),
    ])

    set_layout(df, fig)

    return fig
    

def get_custom_data(df):    
    # Organize custom data for the hover display
    rank_dict = {key: get_rank(df[key]) for key in df.columns}

    # Organize custom data for a rate change bar chart
    custom_data = np.stack((
        df["date"],                                             #0

        df["mentions"],                                         #1
        df["positive"],                                         #2
        df["negative"],                                         #3
        df["neutral"],                                          #4
        
        [ordinal(n) for n in rank_dict["mentions"]],            #5
        [ordinal(n) for n in rank_dict["positive"]],            #6
        [ordinal(n) for n in rank_dict["negative"]],            #7
        [ordinal(n) for n in rank_dict["neutral"]],             #8

        df["total_mentions"],                                   #9
        df["total_positive"],                                   #10
        df["total_negative"],                                   #11
        df["total_neutral"],                                    #12
        
        [ordinal(n) for n in rank_dict["total_mentions"]],      #13
        [ordinal(n) for n in rank_dict["total_positive"]],      #14
        [ordinal(n) for n in rank_dict["total_negative"]],      #15
        [ordinal(n) for n in rank_dict["total_neutral"]],       #16
    ), axis=-1)

    hover_template = """
    <b>%{x}</b><br><br>
    <b>%{customdata[0]}:</b><br>
    Mentions: %{customdata[1]:d} (%{customdata[5]})<br>
    Positive Mentions: %{customdata[2]:d} (%{customdata[6]})<br>
    Negative Mentions: %{customdata[3]:d} (%{customdata[7]})<br>
    Neutral Mentions: %{customdata[4]:d} (%{customdata[8]})<br><br>
    <b>Total:</b><br>
    Total Mentions: %{customdata[9]:d} (%{customdata[13]})<br>
    Positive Mentions: %{customdata[10]:d} (%{customdata[14]})<br>
    Negative Mentions: %{customdata[11]:d} (%{customdata[15]})<br>
    Neutral Mentions: %{customdata[12]:d} (%{customdata[16]})<br>
    <extra></extra>
    """

    return custom_data, hover_template


# Append the trace data
def create_bar_trace(ydata, xdata, name, customdata="", hovertemplate=""):
    trace = go.Bar(
        name=name,
        x=xdata,
        y=ydata,
        customdata=customdata,
        hovertemplate=hovertemplate,
    )

    return trace


def set_layout(df, fig):
    # Create the layout
    date = parse_date(df)

    legend = go.layout.Legend(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.75
    )

    margin = go.layout.Margin(
        l=50,
        r=50,
        b=100,
        t=65,
        pad=4
    )

    fig.update_layout(
        title=f"<b>Overal Daily Sentiment - {date}</b><br>Global Media",
        barmode="stack",
        width=850,
        height=600,
        margin=margin,
        legend=legend,
        xaxis=dict(tickmode='linear'), #Needed to ensure all xticks are shown.
    )

    fig.update_xaxes(
        title_text="Tickers", 
    )

    fig.update_yaxes(
        title_text="Mentions", 
    );


def parse_date(df):
    date_strs  = [df["date"].min(), df["date"].max()]

    return " to ".join(date_strs)


def get_rank(ds: pd.Series):
    return ds.rank(ascending=False).values.astype(int)


def ordinal(n: int):
    return "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
