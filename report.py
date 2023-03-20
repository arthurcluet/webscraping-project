# 0 20 * * *
# Le fichier s'executera tous les jours à 20H
# Le fichier créé un nouveau rapport avec toutes les valeurs entre 8PM de la veille et 8PM d'aujourd'hui
# Le rapport est ajouté a la liste de rapports dans le fichier reports.json
# Enfin, le dashboard affiche le dernier rapport créé et se mettra donc à jour à 20H chaque jour

import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

f = open('/home/arthur/webscraping-project/data/reports.json')
reports = json.load(f)

def mapFunction(x):
    try:
        return float(x.replace(' ', '').replace('$', '').replace(',', '')) if isinstance(x, str) else x 
    except:
        return np.nan
files = {
    "ADA": "/home/arthur/webscraping-project/data/coindesk_ada.txt",
    "BTC": "/home/arthur/webscraping-project/data/coinpaprika_btc.txt",
    "ETH": "/home/arthur/webscraping-project/data/coinmarketcap_eth.txt"
}
def readPrices(coin):
    df = pd.read_csv(files[coin], sep=";", names=["date", coin])
    df[coin] = df[coin].map(mapFunction)
    df = df.dropna()
    return df

now = datetime.now()

def mapLast24H(x):
    dt = datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S')
    if dt.date().day == now.date().day and dt.time().hour < 20:
        return True
    elif (dt + timedelta(days=1)).date().day == now.date().day and dt.time().hour >= 20:
        return True    
    else:
        return False

report = {
    "date": now.strftime("%Y-%m-%d %H:%M:%S")
}

for k in files:
    df = readPrices(k)
    df = df[df.apply(mapLast24H, axis=1)]
    # We got all the data from yesterday 8PM here (and not the last 24 hours)
    #print("************ " + k + " ************")
    #print("Mean:", df[k].mean())
    #print("Vol:", df[k].std())
    #print("Min:", df[k].min())
    #print("Max:", df[k].max())
    initial = df.iloc[0][k]
    final = df.iloc[-1][k]
    #print("Initial value:", initial)
    #print("Final value:", final)
    #print("Evolution", str(round(100*(final-initial)/initial, 2)) + "%")
    report[k] = {
        "mean": df[k].mean(),
        "std": round(df[k].std(), 4),
        "min": df[k].min(),
        "max": df[k].max(),
        "open": initial,
        "close": final,
        "evol": round(100*(final-initial)/initial, 4),
    }
    
reports.append(report)
json_object = json.dumps(reports, indent=4)
    # Writing to sample.json
with open("/home/arthur/webscraping-project/data/reports.json", "w") as outfile:
    outfile.write(json_object)