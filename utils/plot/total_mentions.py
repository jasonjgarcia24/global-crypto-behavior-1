import numpy  as np
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path


def mentions_bar(df, tickers=[]):
    df         = df[df["ticker"].isin(tickers)]
    df         = df.sort_values("ticker", ascending=True)
    df.columns = [str(col.lower()).replace(" ", "_") for col in df.columns]

    customdata, hovertemplate = get_custom_data(df)

    fig = go.Figure([
        create_bar_trace(df["positive_mentions"], df["ticker"], "Positive Mentions", customdata=customdata, hovertemplate=hovertemplate),
        create_bar_trace(df["negative_mentions"], df["ticker"], "Negative Mentions", customdata=customdata, hovertemplate=hovertemplate),
        create_bar_trace(df["neutral_mentions"],  df["ticker"], "Neutral Mentions",  customdata=customdata, hovertemplate=hovertemplate),
    ])

    set_layout(df, fig)

    return fig
    

def get_custom_data(df):    
    # Organize custom data for the hover display
    rank_dict = {key: get_rank(df[key]) for key in df.columns}

    # Organize custom data for a rate change bar chart
    custom_data = np.stack((
        df["name"],                                           #0

        df['total_mentions'],                                 #1
        df['positive_mentions'],                              #2
        df['negative_mentions'],                              #3
        df['neutral_mentions'],                               #4
        
        [ordinal(n) for n in rank_dict["total_mentions"]],    #5
        [ordinal(n) for n in rank_dict["positive_mentions"]], #6
        [ordinal(n) for n in rank_dict["negative_mentions"]], #7
        [ordinal(n) for n in rank_dict["neutral_mentions"]],  #8
        
        df["sentiment_score"],                                #9
        [ordinal(n) for n in rank_dict["sentiment_score"]],   #10
    ), axis=-1)

    hover_template = """
    <b>%{customdata[0]} (%{x})</b><br><br>
    Total Mentions: %{customdata[1]:d} (%{customdata[5]})<br>
    Positive Mentions: %{customdata[2]:d} (%{customdata[6]})<br>
    Negative Mentions: %{customdata[3]:d} (%{customdata[7]})<br>
    Neutral Mentions: %{customdata[4]:d} (%{customdata[8]})<br>
    Sentiment Score: %{customdata[9]:.2f} (%{customdata[10]})<br>
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
    date_range = list(set([df.loc[:,"from_date"].min(), df.loc[:,"to_date"].max()]))
    date_strs  = list(pd.to_datetime(date_range, format="%m%d%Y").strftime("%d-%b-%Y"))

    return " to ".join(date_strs)


def get_rank(ds: pd.Series):
    return ds.rank(ascending=False).values.astype(int)


def ordinal(n: int):
    return "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
