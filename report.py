# 0 20 * * *
# Le fichier s'executera tous les jours à 20H
# Le fichier créé un nouveau rapport avec toutes les valeurs entre 8PM de la veille et 8PM d'aujourd'hui
# Le rapport est ajouté a la liste de rapports dans le fichier reports.json
# Enfin, le dashboard affiche le dernier rapport créé et se mettra donc à jour à 20H chaque jour
# Un rapport peut être créé à n'importe quel moment en executant ce fichier et sera alors affiché sur le dashboard

import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Liste des rapports actuels
# J'ai choisi de lire cette liste et y ajouter le nouveau rapport plutôt qu'écraser les anciens à chaque fois
f = open('/home/arthur/webscraping-project/data/reports.json')
reports = json.load(f)

# Fonction pour parser le prix (s'il contient des virgules, dollars, ...)
# De temps en temps on récupère une valeur invalide et cette fonction permet de le transformer en NaN
def mapFunction(x):
    try:
        return float(x.replace(' ', '').replace('$', '').replace(',', '')) if isinstance(x, str) else x 
    except:
        return np.nan

# Fichiers contenant les différents cours
files = {
    "ADA": "/home/arthur/webscraping-project/data/coindesk_ada.txt",
    "BTC": "/home/arthur/webscraping-project/data/coinpaprika_btc.txt",
    "ETH": "/home/arthur/webscraping-project/data/coinmarketcap_eth.txt"
}

# Fonction de lecture de l'historique d'un cours (les fichiers créés avec le scraper)
def readPrices(coin):
    df = pd.read_csv(files[coin], sep=";", names=["date", coin])
    df[coin] = df[coin].map(mapFunction)
    df = df.dropna()
    return df

# Fonction pour récupérer uniquement les données depuis 8H du soir la veille
now = datetime.now()
def mapLast24H(x):
    dt = datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S')
    # Si il est plus de 20H on prend les prix de la veille et du jour jusqu'à 20H
    if now.time().hour >= 20:
        if dt.date().day == now.date().day and dt.time().hour < 20:
            return True
        elif (dt + timedelta(days=1)).date().day == now.date().day and dt.time().hour >= 20:
            return True    
        else:
            return False
    # Sinon on prend les prix de l'avant veille dès 20h jusqu'à hier 20H
    else:
        if (dt + timedelta(days=1)).date().day == now.date().day and dt.time().hour < 20:
            return True
        elif (dt + timedelta(days=2)).date().day == now.date().day and dt.time().hour >= 20:
            return True    
        else:
            return False

# Objet auquel on ajoute le rapport quotidien
report = {
    "date": now.strftime("%Y-%m-%d %H:%M:%S")
}

# Pour chaque crypto, on créé une nouvelle clé dans notre rapport contenant l'évolution du prix, la volatilité, ect ...
for k in files:
    df = readPrices(k)
    df = df[df.apply(mapLast24H, axis=1)]
    initial = {
        "val": df.iloc[0][k],
        "date": df.iloc[0]['date']
    }
    final = {
        "val": df.iloc[-1][k],
        "date": df.iloc[-1]['date']
    }
    report[k] = {
        "mean": df[k].mean(),
        "std": round(df[k].std(), 4),
        "min": df[k].min(),
        "max": df[k].max(),
        "open": initial,
        "close": final,
        "evol": round(100*(final['val']-initial['val'])/initial['val'], 4),
    }
    
# On ajoute le rapport créé à la liste des rapports précédents
reports.append(report)

# On écrit le résultat dans un fichier
json_object = json.dumps(reports, indent=4)
with open("/home/arthur/webscraping-project/data/reports.json", "w") as outfile:
    outfile.write(json_object)