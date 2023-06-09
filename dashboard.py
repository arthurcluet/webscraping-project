from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import json
import plotly.graph_objects as go

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

def candlestickData(coin):
    import pandas as pd
    cs_df = pd.read_csv(files[coin], sep=";", names=["date", 'price'])
    cs_df['price'] = cs_df['price'].map(mapFunction)
    cs_df = cs_df.dropna()

    # Converti les dates
    cs_df['cs_date'] = pd.to_datetime(cs_df['date'])
    cs_df['cs_date_only'] = cs_df['cs_date'].dt.date
    cs_results_df = pd.DataFrame(columns=['cs_date', 'cs_open_price', 'cs_close_price', 'cs_max_price', 'cs_min_price'])
    for cs_date in cs_df['cs_date_only'].unique():
        cs_current_date_df = cs_df[cs_df['cs_date_only'] == cs_date]
        cs_open_price = cs_current_date_df['price'].iloc[0]
        cs_close_price = cs_current_date_df[cs_df['cs_date_only'] == cs_date]['price'].iloc[-1]
        cs_max_price = cs_current_date_df['price'].max()
        cs_min_price = cs_current_date_df['price'].min()
        cs_results_df = cs_results_df.append({
            'cs_date': cs_date,
            'cs_open_price': cs_open_price,
            'cs_close_price': cs_close_price,
            'cs_max_price': cs_max_price,
            'cs_min_price': cs_min_price
        }, ignore_index=True)
    return cs_results_df


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
            html.Div(children='Simple Moving Average (SMA) periods:', className="label"),
            #html.Div(children=[
                #html.Span('Increase SMA period below to display bollinger bands on the graph. Choose 0 to hide them.'),
                #html.Br(),
                #html.Span('Note: Lines can be hidden by clicking on the legend.')
            #], className='help'),
            dcc.Slider(min=0, max=200, step=1, value=100, className="slider", id="sma-slider", marks={0: '0', 200:'200'}, tooltip={"placement": "bottom", "always_visible": True}),
            html.Div(children='Bollinger bands Δ (in formula μ ± Δ × σ):', className="label"),
            dcc.Slider(min=0.4, max=5, step=0.01, value=2, className="slider", id="delta-slider", marks={0.4: '0.4', 5:'5'}, tooltip={"placement": "bottom", "always_visible": True})
        ])
    ]),

    # Graph
    dcc.Graph(
        id='price-graph'
    ),

    html.Div(className="description", children='''
        Candlesticks showing open/close/max/min price of the selected cryptocurrency (made from 00:00 to 23:59 and not 8pm)
    '''),

    dcc.Graph(
        id='candle-graph'
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
                Output('candle-graph', 'figure'),
              Input('interval-component', 'n_intervals'),
              Input('coin-dropdown', 'value'),
              Input('sma-slider', 'value'),
              Input('delta-slider', 'value'))
def update_graph(n, value, sma, delta):
    # Lecture des prix de la crypto choisie

    #delta = 1

    df = readPrices(value)
    y = [value]

    # Création du graph
    fig = px.line(df, x='date', y=y)

    # Ajout de la moyenne mobile (si voulue)
    if sma > 0:
        df['SMA'] = df[value].rolling(sma).mean()
        if sma > 1:
            df['STD'] = df[value].rolling(sma).std()
            df['bb_low'] = df['SMA'] - delta * df['STD']
            df['bb_up'] = df['SMA'] + delta * df['STD']

            fig.add_trace(go.Scatter(x=df['date'], y=df['bb_up'],
                fill=None,
                mode='lines',
                line_color='lightgreen', name="Upper band"
                ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['bb_low'],
                fill='tonexty', # fill area between trace0 and trace1
                mode='lines', line_color='lightgreen', name="Lower band"))

            #fig.add_scatter(x=df['date'], y=df['bb_up'], mode='lines', name="Upper band")
            #fig.add_scatter(x=df['date'], y=df['bb_low'], mode='lines', name="Lower band")
        if sma == 1:
            df.dropna(inplace=True)
        fig.add_scatter(x=df['date'], y=df['SMA'], mode='lines', name="SMA", line_color="red")
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

    # FontAwesome Icons
    bitcoinIcon = html.I(className="fa-brands fa-bitcoin")
    chartLineIcon = html.I(className="fa-solid fa-chart-line")
    evolutionIcon = html.I(className="fa-solid " + ("fa-caret-up" if report[value]['evol'] > 0 else "fa-caret-down"))
    backwardStepIcon = html.I(className="fa-solid fa-backward-step")
    forwardStepIcon = html.I(className="fa-solid fa-forward-step")
    volatilityIcon = html.I(className="fa-solid fa-arrow-down-up-across-line")
    downIcon = html.I(className="fa-solid fa-down-long")
    upIcon = html.I(className="fa-solid fa-up-long")

    # Couleur pour l'évolution du prix
    evolutionColor = "green" if report[value]['evol'] > 0 else "red"

    # Raccourci pour crééer un span avec la classe "bold"
    def boldSpan(content):
        return html.Span(className="bold", children=content)

    # Valeurs à afficher
    openPrice = boldSpan("$" + str('{:,}'.format(report[value]['open']['val'])))
    openPriceDate = (" ("+ report[value]['open']['date'] +")")
    closePrice = boldSpan("$" + str('{:,}'.format(report[value]['close']['val'])))
    closePriceDate = (" ("+ report[value]['close']['date'] +")")
    minimumPrice = boldSpan("$" + str('{:,}'.format(report[value]['min'])))
    maximumPrice = boldSpan("$" + str('{:,}'.format(report[value]['max'])))
    
    # Tableau
    tableContent = [
        html.Tr(children=[
            html.Td(children=[bitcoinIcon, "Currency"]),
            html.Td(id="reportCurrency", children=boldSpan(value))]),
        html.Tr(children=[
            html.Td(children=[chartLineIcon, "Evolution"]),
            html.Td(id="reportEvolution", className=evolutionColor, children=[
                evolutionIcon,
                boldSpan((str(report[value]['evol']) + "%"))
            ])]),
        html.Tr(children=[
            html.Td(children=[backwardStepIcon,"Open price"]),
            html.Td(id="reportOpen", children=[openPrice, openPriceDate])]),
        html.Tr(children=[
            html.Td(children=[forwardStepIcon,"Close price"]),
            html.Td(id="reportClose", children=[closePrice, closePriceDate])]),
        html.Tr(children=[
            html.Td(children=[volatilityIcon, "Volatility"]),
            html.Td(id="reportVol", children=boldSpan(report[value]['std']))]),
        html.Tr(children=[
            html.Td(children=[downIcon, "Minimum"]),
            html.Td(id="reportMin", children=minimumPrice)]),
        html.Tr(children=[
            html.Td(children=[upIcon, "Maximum"]),
            html.Td(id="reportMax", children=maximumPrice)]),
    ]

    candle = candlestickData(value)
    figCandle = go.Figure(data=[go.Candlestick(x=candle['cs_date'],
                open=candle['cs_open_price'],
                high=candle['cs_max_price'],
                low=candle['cs_min_price'],
                close=candle['cs_close_price'])])
    figCandle.update_layout(xaxis_rangeslider_visible=False)

    # Renvoi des valeurs modifiées
    return fig, tableContent, livePriceDiv, reportDate, figCandle

# Lancement du dashboard
if __name__ == '__main__':
    app.run_server(debug=False, port=3000, host= '0.0.0.0')