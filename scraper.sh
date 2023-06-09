#!/bin/bash

# Path where the script is
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# Getting values from websites

# Curl classique sans afficher le chargement avec l'option silent
# J'utilise ensuite "grep -o -P '(?<=DEBUT).*(?=FIN)'" pour chercher la valeur entre deux mots
cd_ada=$(curl -s https://www.coindesk.com/price/cardano/ |  grep -o -P '(?<=<span class=\"currency-pricestyles__Price-sc-1rux8hj-0 jxzQXk\">).*(?=</span></div><div class=\"Box-sc-1hpkeeg-0 bWliNl)')
# J'ai utilisé le flag --compressed puisque CoinMarketCap utilise la compression pour rendre le chargement du site plus rapide
# J'utilise ensuite "grep -o -P '(?<=DEBUT).*(?=FIN)'" pour chercher la valeur entre deux mots
# J'enlève la virgule et le $ avec sed
cmc_eth=$(curl -s --compressed https://coinmarketcap.com/currencies/ethereum/ |  grep -o -P '(?<=<div class=\"priceValue \"><span>).*(?=</span></div><span style=)' | sed -e 's/,//g' -e 's/\$//g')
# Sur ce site, le prix est sur une ligne juste après la ligne contenant la balise span.CoinPrice
# J'ai donc choisi de chercher la balise et afficher la ligne suivant le résultat
# Et enfin garder uniquement la dernière ligne entre les deux avec tail
# Enfin, avec sed je supprime le signe $ et l'espace
cp_btc=$(curl -s https://coinpaprika.com/coin/btc-bitcoin/ |  grep -A 1 '<span id=\"coinPrice\"' | tail -1 | sed -e 's/ //g' -e 's/\$//g')

# Saving values into files
echo "$(date +'%Y-%m-%d %H:%M:%S');$cd_ada" >> $parent_path/data/coindesk_ada.txt
echo "$(date +'%Y-%m-%d %H:%M:%S');$cmc_eth" >> $parent_path/data/coinmarketcap_eth.txt
echo "$(date +'%Y-%m-%d %H:%M:%S');$cp_btc" >> $parent_path/data/coinpaprika_btc.txt

# Colors for echo (not used yet)
NC='\033[0m'
YELLOW='\033[1;33m'

# Manual
# There is not option yet but it can be an improvement in a future... a verbose option? silent option? 
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]
then
	echo "ABOUT"
	echo -e "  This script downloads a page containing current bitcoin price and saves\n  the new price in a file on a new line.\n"
    echo "PARAMETERS"
	echo "  No parameters yet"
fi
