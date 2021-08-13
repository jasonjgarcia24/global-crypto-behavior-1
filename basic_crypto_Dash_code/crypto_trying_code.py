import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import dash  
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)


data ={ 
        'price': [ .67,.45,.32,.22], 
        'transactions': [785,345,222,100 ], 
        'country': ['America', 'Nigeria', 'Philippines','China'],
        'date':['2021','2020', '2021','2020'],
        'name':['BTC','Ethereum', 'Cardona', 'Litecoin'] }

crypto =pd.DataFrame(data)      
crypto = crypto.groupby(['name','country','date','price'])[['transactions']] 





print(crypto)

app.layout = html.Div([
    
    html.H1("Global Crypto Behavior", style={'text-align': 'center'}),
    #html.H3('Global Crypto Behavior', style={'margin-bottom': '20px', 'color': 'white'}),

    dcc.Dropdown(id="name_symbol",
                 options=[
                     {"label": "Bitcoin", "value": 'BTC'},
                     {"label": "Ethereum", "value":'ETH'},
                     {"label": "Cardano", "value":'ADA'},
                     {"label": "Litecoin", "value":'LTC'}],
                 multi=False,
                 value='BTC',
                 style={'width': "40%"}
                 ),
    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='crypto_map', figure={})

])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='crypto_map', component_property='figure')],
    [Input(component_id='name_symbol', component_property='value')]
)
def update_map(option_slctd):
    print(option_slctd)
    print(type(option_slctd))
    
    container = "The year chosen by user was: {}".format(option_slctd)

    crypto_copy = crypto.copy()
    crypto_copy = crypto_copy[crypto_copy["name"] == option_slctd]
    crypto_copy = crypto_copy[crypto_copy["country"] == "China"]

# Plotly Express
    fig = px.choropleth(
        data_frame=crypto_copy,
        locationmode='country names',
        locations=['America','Nigeria','Philippines','China'],
        scope= "world",
        color='transactions',
        hover_data=['country', 'transactions'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'transactions': 'number of exchanges'},
        template='plotly_dark'
    )

#Plotly Graph Objects (GO)
    fig = go.Figure(
        data=[go.Choropleth(
            locationmode='country names',
            locations=crypto_copy['America','Nigeria','Philippines','China'],
            z=crypto_copy["transactions"].astype(float),
            colorscale='Reds',
        )]
    )

    fig.update_layout(
        title_text="Global Crypto Exchange",
        title_xanchor="center",
        title_font=dict(size=24),
        title_x=0.5,
        geo=dict(scope='world'),
    )

    return container, fig

if __name__ == '__main__':
    app.run_server()