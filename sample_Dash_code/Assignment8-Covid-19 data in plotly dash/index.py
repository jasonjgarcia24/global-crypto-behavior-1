import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import date


covid = pd.read_csv('covid_19_clean_complete.csv')
covid['Date'] = pd.to_datetime(covid['Date'])





app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.H3('World Covid-19 Data', style = {'margin-bottom': '20px', 'color': 'white'}),
            ])
        ], className = "create_container1 four columns", id = "title"),

    ], id = "header", className = "row flex-display", style = {"margin-bottom": "25px"}),



      html.Div([
        html.Div([
            html.P('Select Country', className = 'fix_label', style = {'color': 'white'}),
            dcc.Dropdown(id = 'select_country',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         value = 'US',
                         placeholder = 'Select Countries',
                         options = [{'label': c, 'value': c}
                                    for c in (covid['Country/Region'].unique())], className = 'dcc_compon'),

            html.P('Select Date', className = 'fix_label', style = {'color': 'white', 'margin-top': '40px'}),
            dcc.DatePickerRange(
                        id='date_range',
                        day_size = 50,
                        reopen_calendar_on_clear=True,
                        clearable = True,
                        min_date_allowed = date(2020, 1, 1),
                        max_date_allowed = date(2020, 12, 31),
                        # initial_visible_month = date(2020, 7, 1),
                        start_date = date(2020, 6, 1),
                        end_date = date(2020, 6, 30),
                        minimum_nights = 0,
                        updatemode = 'singledate'
                        , className = 'dcc_compon'),

        ], className = "create_container2 five columns"),





        html.Div([
            dcc.Graph(id = 'pie_chart',
                      config = {'displayModeBar': 'hover'}),

        ], className = "create_container2 six columns"),

    ], className = "row flex-display"),

], id= "mainContainer", style={"display": "flex", "flex-direction": "column"})


@app.callback(Output('pie_chart', 'figure'),
              [Input('select_country', 'value')],
              [Input('date_range', 'start_date')],
              [Input('date_range', 'end_date')])
def update_graph(select_country, start_date, end_date):
    covid1 = covid.groupby(['Date', 'Country/Region'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()
    covid2 = covid1[covid1['Country/Region'] == select_country][['Country/Region', 'Date', 'Confirmed']].reset_index()
    covid2['daily confirmed'] = covid2['Confirmed'] - covid2['Confirmed'].shift(1)
    covid2.fillna(0, inplace = True)
    daily_confirmed = covid2[(covid2['Country/Region'] == select_country) & (covid2['Date'].between(start_date, end_date))]['daily confirmed'].sum()

    covid3 = covid.groupby(['Date', 'Country/Region'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()
    covid4 = covid3[covid3['Country/Region'] == select_country][['Country/Region', 'Date', 'Deaths']].reset_index()
    covid4['daily deaths'] = covid4['Deaths'] - covid4['Deaths'].shift(1)
    covid4.fillna(0, inplace = True)
    daily_deaths = covid4[(covid4['Country/Region'] == select_country) & (covid4['Date'].between(start_date, end_date))]['daily deaths'].sum()

    covid5 = covid.groupby(['Date', 'Country/Region'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()
    covid6 = covid5[covid5['Country/Region'] == select_country][['Country/Region', 'Date', 'Recovered']].reset_index()
    covid6['daily recovered'] = covid6['Recovered'] - covid6['Recovered'].shift(1)
    covid6.fillna(0, inplace = True)
    daily_recovered = covid6[(covid6['Country/Region'] == select_country) & (covid6['Date'].between(start_date, end_date))]['daily recovered'].sum()

    covid7 = covid.groupby(['Date', 'Country/Region'])[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum().reset_index()
    covid8 = covid7[covid7['Country/Region'] == select_country][['Country/Region', 'Date', 'Active']].reset_index()
    covid8['daily active'] = covid8['Active'] - covid8['Active'].shift(1)
    covid8.fillna(0, inplace = True)
    daily_active = covid8[(covid8['Country/Region'] == select_country) & (covid8['Date'].between(start_date, end_date))]['daily active'].sum()

    colors = ['orange', '#dd1e35', 'green', '#e55467']

    return {
        'data': [go.Pie(labels = ['Confirmed', 'Deaths', 'Recovered', 'Active'],
                        values = [daily_confirmed, daily_deaths, daily_recovered, daily_active],
                        marker = dict(colors = colors),
                        hoverinfo = 'label+value+percent',
                        textinfo = 'label+value',
                        textfont = dict(size = 13),
                        texttemplate = '%{label}: %{value:,f} <br>(%{percent})',
                        textposition = 'auto',
                        # hole = .7,
                        rotation = 220
                        # insidetextorientation='radial',

                        )],

        'layout': go.Layout(
            # width=800,
            # height=520,
            plot_bgcolor = '#010915',
            paper_bgcolor = '#010915',
            hovermode = 'x',
            title = {
                'text': 'Total Cases : ' + (select_country) + ' ' + 'from Date' + ' ' + (start_date) + ' ' + 'to' + ' ' + (end_date),

                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = {
                'color': 'white',
                'size': 15},
            legend = {
                'orientation': 'h',
                'bgcolor': '#010915',
                'xanchor': 'center', 'x': 0.5, 'y': -0.07},
            font = dict(
                family = "sans-serif",
                size = 12,
                color = 'white')
        ),

    }

if __name__ == '__main__':
    app.run_server()