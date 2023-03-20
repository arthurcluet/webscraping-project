from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import json


external_scripts = [
    {
        'src': 'https://kit.fontawesome.com/fe63a2ff94.js',
        'crossorigin': 'anonymous'
    }
]


# Function that reads prices from the files
# It removes any unwanted characters from strings such as "$24,393" and parses it as a float
# Then if an error occured and a value can't be used, it just drops the line containing NA

def mapFunction(x):
    try:
        return float(x.replace(' ', '').replace('$', '').replace(',', '')) if isinstance(x, str) else x 
    except:
        return np.nan
files = {
    "ADA": "./data/coindesk_ada.txt",
    "BTC": "./data/coinpaprika_btc.txt",
    "ETH": "./data/coinmarketcap_eth.txt"
}
def readPrices(coin):
    df = pd.read_csv(files[coin], sep=";", names=["date", coin])
    df[coin] = df[coin].map(mapFunction)
    df = df.dropna()
    return df

# Dashboard Layout
app = Dash(__name__, external_scripts=external_scripts)
app.title = "Crypto Prices"

app.layout = html.Div(className="app", children=[
    html.H1(children='Cryptocurrency Prices'),

    html.Div(className="description", children='''
        A dashboard following the evolution of the price of some cryptocurrencies
    '''),

    html.Div(className="row", children=[
        html.Div(className="col", children=[html.Div(children='Cryptocurrency:', className="label"),

    dcc.Dropdown(options=[
       {'label': 'Bitcoin (BTC)', 'value': 'BTC'},
       {'label': 'Ethereum (ETH)', 'value': 'ETH'},
       {'label': 'Cardano (ADA)', 'value': 'ADA'},
   ],
   value='BTC', id='coin-dropdown', searchable=False, clearable=False)]),
        html.Div(className="col", children=[html.Div(children='SMA periods:', className="label"),
    html.Div(children=[
        html.Span('Increase SMA period below to display bollinger bands on the graph. Choose 0 to hide them.'),
        html.Br(),
        html.Span('Note: Lines can be hidden by clicking on the legend.')
    ], className='help'),

   dcc.Slider(min=0, max=200, step=1, value=0, className="slider", id="sma-slider", marks={0: '0', 200:'200'})    ])
    ]),

    
    

    dcc.Graph(
        id='price-graph'
    ),
    dcc.Interval(
            id='interval-component',
            interval=90*1000, # every 90 seconds
            n_intervals=0
        ),


    html.Div(className="row", children=[
        html.Div(className="col", children=[

                html.Div(className="description", children=["Daily report, generated ", html.Span(id="reportDate", children="", className="bold"), " (24h period from 8pm to 8pm)"]),

                html.Div(children=[
                    html.Span('Since there is no opening and closing price for crypto-currencies, the daily report is generated with the price of the crypto-currencies over a 24 hour period since 8pm the previous day. Reports can be generated manually by running a Python script and it will still use 8pm as open and close time.')
                ], className='help'),

                html.Table(children=html.Tbody(children=[
                    html.Tr(children=[html.Td(children=[html.I(className="fa-brands fa-bitcoin"), "Currency"]), html.Td(id="reportCurrency", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-chart-line"), "Evolution"]), html.Td(id="reportEvolution", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-backward-step"),"Open price"]), html.Td(id="reportOpen", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-forward-step"),"Close price"]), html.Td(id="reportClose", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-arrow-down-up-across-line"), "Volatility"]), html.Td(id="reportVol", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-down-long"), "Minimum"]), html.Td(id="reportMin", children="")]),
                    html.Tr(children=[html.Td(children=[html.I(className="fa-solid fa-up-long"), "Maximum"]), html.Td(id="reportMax", children="")]),
                ]))

        ])
    ])
])

# Callback, updates the shown figure depending on two inputs
@app.callback(Output('price-graph', 'figure'),
                Output('reportDate', 'children'),
                Output('reportCurrency', 'children'),
                Output('reportEvolution', 'children'),

                Output('reportOpen', 'children'),
                Output('reportClose', 'children'),

                Output('reportVol', 'children'),

                Output('reportMin', 'children'),
                Output('reportMax', 'children'),

                Output('reportEvolution', 'className'),
                
              Input('interval-component', 'n_intervals'),
              Input('coin-dropdown', 'value'),
              Input('sma-slider', 'value'))
def update_graph(n, value, sma):
    df = readPrices(value)
    #fig = px.line(df, x='date', y=value)
    y = [value]

    fig = px.line(df, x='date', y=y)

    if sma > 0:
        df['SMA'] = df[value].rolling(sma).mean()
        if sma == 1:
            df.dropna(inplace=True)
        fig.add_scatter(x=df['date'], y=df['SMA'], mode='lines', name="SMA")
        if sma > 1:
            delta = 1
            df['STD'] = df[value].rolling(sma).std()
            df['bb_low'] = df['SMA'] - delta * df['STD']
            df['bb_up'] = df['SMA'] + delta * df['STD']
            fig.add_scatter(x=df['date'], y=df['bb_up'], mode='lines', name="Upper band")
            fig.add_scatter(x=df['date'], y=df['bb_low'], mode='lines', name="Lower band")

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))


    f = open('/home/arthur/webscraping-project/data/reports.json')
    report = json.load(f)[-1]

    reportDate = report['date']
    reportEvolution = [html.I(className="fa-solid " + ("fa-caret-up" if report[value]['evol'] > 0 else "fa-caret-down")), html.Span(className="bold", children=(str(report[value]['evol']) + "%"))]
    reportOpen = [html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['open']['val'])))) , (" ("+ report[value]['open']['date'] +")")]
    reportClose = [html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['close']['val'])))) , (" ("+ report[value]['close']['date'] +")")]
    reportVol = html.Span(className="bold", children=(report[value]['std']))
    reportMin = html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['min']))))
    reportMax = html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['max']))))
    reportEvolColor = ("green" if report[value]["evol"] > 0 else "red")

    return fig, reportDate, html.Span(className="bold", children=value), reportEvolution, reportOpen, reportClose, reportVol, reportMin, reportMax, reportEvolColor


if __name__ == '__main__':
    app.run_server(debug=True, port=3000, host= '0.0.0.0')