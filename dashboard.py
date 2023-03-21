from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import json

# Import de Font Awesome pour les icônes
external_scripts = [
    {
        'src': 'https://kit.fontawesome.com/fe63a2ff94.js',
        'crossorigin': 'anonymous'
    }
]

# Fonction pour paser les prix contenant des caractères spéciaux et supprimer les prix invalides
def mapFunction(x):
    try:
        return float(x.replace(' ', '').replace('$', '').replace(',', '')) if isinstance(x, str) else x 
    except:
        return np.nan

# Fichiers contenant les prix
files = {
    "ADA": "./data/coindesk_ada.txt",
    "BTC": "./data/coinpaprika_btc.txt",
    "ETH": "./data/coinmarketcap_eth.txt"
}
# Fonction de lecture des fichiers de prix scrappés
def readPrices(coin):
    df = pd.read_csv(files[coin], sep=";", names=["date", coin])
    df[coin] = df[coin].map(mapFunction)
    df = df.dropna()
    return df

##### TABLEAU DE BORD #####
app = Dash(__name__, external_scripts=external_scripts)
app.title = "Crypto Prices"

# Layout de la page
app.layout = html.Div(className="app", children=[
    # Grand titre
    html.H1(children='Cryptocurrency Prices'),

    # Description
    html.Div(className="description", children='''
        A dashboard following the evolution of the price of some cryptocurrencies
    '''),

    # Ligne contenant deux colonnes
    html.Div(className="row", children=[
        # Colonne avec le sélecteur et le cours actuel
        html.Div(className="col", children=[
            html.Div(children='Cryptocurrency:', className="label"),
            dcc.Dropdown(options=[
                {'label': 'Bitcoin (BTC)', 'value': 'BTC'},
                {'label': 'Ethereum (ETH)', 'value': 'ETH'},
                {'label': 'Cardano (ADA)', 'value': 'ADA'},
            ], value='BTC', id='coin-dropdown', searchable=False, clearable=False),
            html.Div(id="current-price", children=""),
        ]),
        # Colonne avec la possibilité d'ajouter une moyenne mobile
        html.Div(className="col", children=[
            html.Div(children='SMA periods:', className="label"),
            html.Div(children=[
                html.Span('Increase SMA period below to display bollinger bands on the graph. Choose 0 to hide them.'),
                html.Br(),
                html.Span('Note: Lines can be hidden by clicking on the legend.')
            ], className='help'),
            dcc.Slider(min=0, max=200, step=1, value=0, className="slider", id="sma-slider", marks={0: '0', 200:'200'})
        ])
    ]),

    # Graph
    dcc.Graph(
        id='price-graph'
    ),
    # Intervalle pour rafraîchir le contenu automatiquement
    dcc.Interval(
        id='interval-component',
        interval=90*1000, # every 90 seconds
        n_intervals=0
    ),

    # Ligne contenant le tableau avec le rapport
    html.Div(className="row", children=[
        html.Div(className="col", children=[
            # Description
            html.Div(className="description", children=["Daily report, generated ", html.Span(id="reportDate", children="", className="bold"), " (24h period from 8pm to 8pm)"]),

            # Notes
            html.Div(children=[
                html.Span('Since there is no opening and closing price for crypto-currencies, the daily report is generated with the price of the crypto-currencies over a 24 hour period since 8pm the previous day. Reports can be generated manually by running a Python script and it will still use 8pm as open and close time.')
            ], className='help'),

            # Tableau
            html.Table(id="reportTable",children=html.Tbody(children=[]))
        ])
    ])
])

# Callback mettant à jour toute la page
# Inputs : intervalle, slider, sélecteur de crypto
# Outputs : graph, tableau, prix live, ...
@app.callback(Output('price-graph', 'figure'),
                Output('reportTable', 'children'),
                Output('current-price', 'children'),
                Output('reportDate', 'children'),
              Input('interval-component', 'n_intervals'),
              Input('coin-dropdown', 'value'),
              Input('sma-slider', 'value'))
def update_graph(n, value, sma):
    # Lecture des prix de la crypto choisie
    df = readPrices(value)
    y = [value]

    # Création du graph
    fig = px.line(df, x='date', y=y)

    # Ajout de la moyenne mobile (si voulue)
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

    # Paramètres du graph
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    # Affichage du prix live et l'évolution instantannée
    previousPrice = df.iloc[-2][value]
    currentPrice = df.iloc[-1][value]
    liveEvol = 100*(currentPrice - previousPrice)/previousPrice

    # Div pour la valeur live
    livePriceDiv =[ 
        html.Span("$" + str('{:,}'.format(currentPrice)), className="livePrice"),
        html.Span(className="liveEvol " + ("green" if liveEvol > 0 else "red" if liveEvol < 0 else ""), children=[
            html.I(className="fa-solid " + ("fa-caret-up" if liveEvol > 0 else "fa-caret-down" if liveEvol < 0 else "fa-minus")),
            html.Span(str(round(liveEvol, 4)) + "%")
        ])
    ]

    # Lecture des rapports quotidiens
    f = open('/home/arthur/webscraping-project/data/reports.json')
    report = json.load(f)[-1]

    # Lecture de la date
    reportDate = report['date']

    # On met les données dans un tableau
    # Je reconnais que c'est pas très lisible

    # Chaque Tr contient 2 Td
    # Le  1er Td contient - une balise "i" (icône FontAwesome) + la description de la ligne
    # Le 2eme Td contient - la valeur du rapport dans un SPAN

    # Je songe à mettre chaque valeur dans des variables pour simplifier un peu la lecture mais ça fonctionne très bien comme ça et VSCode met les paranthèses correspondantes de la même couleur
    tableContent = [
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-brands fa-bitcoin"), "Currency"]),
            html.Td(id="reportCurrency", children=html.Span(className="bold", children=value))]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-chart-line"), "Evolution"]),
            html.Td(id="reportEvolution", className=("green" if report[value]['evol'] > 0 else "red"), children=[
                html.I(className="fa-solid " + ("fa-caret-up" if report[value]['evol'] > 0 else "fa-caret-down")),
                html.Span(className="bold", children=(str(report[value]['evol']) + "%"))])]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-backward-step"),"Open price"]),
            html.Td(id="reportOpen", children=[html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['open']['val'])))) , (" ("+ report[value]['open']['date'] +")")])]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-forward-step"),"Close price"]),
            html.Td(id="reportClose", children=[html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['close']['val'])))) , (" ("+ report[value]['close']['date'] +")")])]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-arrow-down-up-across-line"), "Volatility"]),
            html.Td(id="reportVol", children=html.Span(className="bold", children=(report[value]['std'])))]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-down-long"), "Minimum"]),
            html.Td(id="reportMin", children=html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['min'])))))]),
        html.Tr(children=[
            html.Td(children=[html.I(className="fa-solid fa-up-long"), "Maximum"]),
            html.Td(id="reportMax", children=html.Span(className="bold", children=("$" + str('{:,}'.format(report[value]['max'])))))]),
    ]

    # Renvoi des valeurs modifiées
    return fig, tableContent, livePriceDiv, reportDate

# Lancement du dashboard
if __name__ == '__main__':
    app.run_server(debug=True, port=3000, host= '0.0.0.0')