import numpy  as np
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path


class StatsBar():
    def __init__(self, data_path="", df=pd.DataFrame(), dates=None):
        self.data_path = data_path

        self.__set_df(df)
        self.__set_fig(self.df)
        self.__set_layout()

    @property
    def show(self):
        return self.fig.show

    def __set_df(self, df):
        if self.data_path:
            df = pd.read_csv(self.data_path)

        df["sentiment_score"].name = "this_sentiment_score"

        df.columns = [str(col.lower()).replace(" ", "_") for col in df.columns]
        df["mentions"] = df.loc[:, ["positive", "negative", "neutral"]].sum(axis=1)

        for ticker in df["ticker"].unique():
            df.loc[df["ticker"]==ticker, "total_mentions"] = df.loc[df["ticker"]==ticker, "mentions"].sum()
            df.loc[df["ticker"]==ticker, "total_positive"] = df.loc[df["ticker"]==ticker, "positive"].sum()
            df.loc[df["ticker"]==ticker, "total_negative"] = df.loc[df["ticker"]==ticker, "negative"].sum()
            df.loc[df["ticker"]==ticker, "total_neutral"]  = df.loc[df["ticker"]==ticker, "neutral" ].sum()

        df = df.sort_values(["ticker", "date"], ascending=True)

        self.df = df

    def __set_fig(self, df):
        customdata, hovertemplate = self.__get_custom_data(df)

        self.fig = go.FigureWidget([
            self.__create_bar_trace(df["positive"], df["ticker"], "Positive Mentions", customdata=customdata, hovertemplate=hovertemplate),
            self.__create_bar_trace(df["negative"], df["ticker"], "Negative Mentions", customdata=customdata, hovertemplate=hovertemplate),
            self.__create_bar_trace(df["neutral"],  df["ticker"], "Neutral Mentions",  customdata=customdata, hovertemplate=hovertemplate),
        ])

    def __set_layout(self):
        # Create the layout
        date = self.__parse_date(self.df)

        legend = go.layout.Legend(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.75
        )

        margin = go.layout.Margin(
            l=20,
            r=20,
            b=20,
            t=65,
            pad=4
        )

        self.fig.update_layout(
            title={
                "text": f"<b>Overal Daily Sentiment - {date}</b><br>Global Media",
                "font": dict(size=13),
            },
            barmode="stack",
            margin=margin,
            legend=legend,
            xaxis=dict(tickmode='linear'), #Needed to ensure all xticks are shown.
        )

        self.fig.update_xaxes(
            title={
                "text": "<i>Tickers</i>",
                "font": dict(size=12),
            }
        )

        self.fig.update_yaxes(
            title={
                "text": "<i>Mentions</i>",
                "font": dict(size=12),
            }
        );

    def trim_dates(self, dates):
        if not dates:
            return
        elif not isinstance(dates, (list, tuple)):
            dates = [dates,]

        formatted_dates = self.series_time_formatter(self.df["date"])
        df = self.df.loc[formatted_dates.isin(dates)]

        self.__set_fig(df)
        self.__set_layout()

    @classmethod
    def __get_custom_data(cls, df):    
        # Organize custom data for the hover display
        rank_dict = {key: cls.__get_rank(df[key]) for key in df.columns}

        # Organize custom data for a rate change bar chart
        custom_data = np.stack((
            df["date"],                                                 #0

            df["mentions"],                                             #1
            df["positive"],                                             #2
            df["negative"],                                             #3
            df["neutral"],                                              #4
            
            [cls.__ordinal(n) for n in rank_dict["mentions"]],         #5
            [cls.__ordinal(n) for n in rank_dict["positive"]],         #6
            [cls.__ordinal(n) for n in rank_dict["negative"]],         #7
            [cls.__ordinal(n) for n in rank_dict["neutral"]],          #8

            df["total_mentions"],                                       #9
            df["total_positive"],                                       #10
            df["total_negative"],                                       #11
            df["total_neutral"],                                        #12
            
            [cls.__ordinal(n) for n in rank_dict["total_mentions"]],   #13
            [cls.__ordinal(n) for n in rank_dict["total_positive"]],   #14
            [cls.__ordinal(n) for n in rank_dict["total_negative"]],   #15
            [cls.__ordinal(n) for n in rank_dict["total_neutral"]],    #16
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
    @staticmethod
    def __create_bar_trace(ydata, xdata, name, customdata="", hovertemplate=""):
        trace = go.Bar(
            name=name,
            x=xdata,
            y=ydata,
            customdata=customdata,
            hovertemplate=hovertemplate,
        )

        return trace

    @staticmethod
    def __parse_date(df):
        date_strs  = [df["date"].min(), df["date"].max()]

        return " to ".join(date_strs)

    @staticmethod
    def series_time_formatter(dates: pd.Series):
        return pd.to_datetime(dates, infer_datetime_format=True).dt.strftime("%Y-%b-%d")

    @staticmethod
    def __get_rank(ds: pd.Series):
        return ds.rank(ascending=False).values.astype(int)

    @staticmethod
    def __ordinal(n: int):
        return "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
