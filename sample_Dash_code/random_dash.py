import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import pandas as pd
import plotly.express as px


 
app = dash.Dash(__name__)

practice_random = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))



practice_random.rename(columns = {'A':'name', 'B':'date_added', 'C':'quote','D':'total_supply'})

print(practice_random)

app.layout = html.Div([
    html.Div([dcc.Dropdown(id='crypto_news', options=[{'label': i, 'value': i} for i in practice_random],
                           value='name', style={'width': '140px'})]),
    dcc.Graph('crypto-dashboard ', config={'displayModeBar': False})]
)



#@app.callback(
    #Output('crypto-dashboard', 'figure'),
    #[Input('crypto_news', 'value')]
#)

#def update_graph(grpname):
    
    #return px.scatter(practice_random[practice_random.group == grpname], x='min_mid', y='player', size='shots_freq', color='pl_pps')
#app.scripts.config.serve_locally = True
#app.css.config.serve_locally = True





if __name__ == '__main__':
    app.run_server()

     