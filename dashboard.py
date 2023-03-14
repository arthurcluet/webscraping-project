from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = Dash(__name__)


def readData():
    f = open("./data/coinmarketcap_eth.txt","r")
    lines = f.readlines()
    def getDates(s):
        return s.split('|')[0].replace(',', '').replace('\n', '')
    def getVal(s):
        return float(s.split('|')[1].replace(',', '').replace('\n', '').replace('$', ''))
    dataDates = list(map(getDates, lines))
    dataValues = list(map(getVal, lines))
    return pd.DataFrame({'date':dataDates, 'ETH':dataValues})

app.layout = html.Div(className="app", children=[
    html.H1(children='Ethereum Price'),

    html.Div(className="description", children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='price-graph'
    ),
    dcc.Interval(
            id='interval-component',
            interval=30*1000, # every 30 seconds
            n_intervals=0
        )
])

@app.callback(Output('price-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph(n):
    bitcoinDf = readData()
    fig = px.line(bitcoinDf, x='date', y="ETH")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=3000, host= '0.0.0.0')