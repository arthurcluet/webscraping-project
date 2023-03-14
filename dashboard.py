from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = Dash(__name__)

def readData():
    f = open("./data/bitcoin-history.txt","r")
    lines = f.readlines()
    def getDates(s):
        return s.split('|')[0].replace(',', '').replace('\n', '')
    def getVal(s):
        return s.split('|')[1].replace(',', '').replace('\n', '')
    dataDates = list(map(getDates, lines))
    dataValues = list(map(getVal, lines))
    return pd.DataFrame({'date':dataDates, 'BTC':dataValues})

app.layout = html.Div(children=[
    html.H1(children='Bitcoin Price'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph'
    ),
    dcc.Interval(
            id='interval-component',
            interval=30*1000, # every 30 seconds
            n_intervals=0
        )
])

@app.callback(Output('example-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph(n):
    bitcoinDf = readData()
    fig = px.line(bitcoinDf, x='date', y="BTC")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=3000, host= '0.0.0.0')