#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# Downloading differents values
curl -s https://www.coingecko.com/en/coins/bitcoin > "$parent_path/data/coingecko_btc.html"
curl -s --compressed https://coinmarketcap.com/currencies/ethereum/ > "$parent_path/data/coinmarketcap_eth.html"
curl -s https://coinpaprika.com/coin/btc-bitcoin/ > "$parent_path/data/coinpaprika_btc.html"

# Getting value from HTML
bitcoin=$(cat $parent_path/data/coingecko_btc.html |  grep -o -P '(?<=\$).*(?=</span></span>)' | head -1)
cmc_eth=$(cat $parent_path/data/coinmarketcap_eth.html |  grep -o -P '(?<=<div class=\"priceValue \"><span>).*(?=</span></div><span style=)' | head -1)
cp_btc=$(cat $parent_path/data/coinpaprika_btc.html |  grep -A 1 '<span id=\"coinPrice\"' | tail -1 )

# Saving value into a file
echo "$(date +'%Y-%m-%d %H:%M:%S')|$bitcoin" >> $parent_path/data/coingecko_btc.txt
echo "$(date +'%Y-%m-%d %H:%M:%S')|$cmc_eth" >> $parent_path/data/coinmarketcap_eth.txt
echo "$(date +'%Y-%m-%d %H:%M:%S')|$cp_btc" >> $parent_path/data/coinpaprika_btc.txt

# Adding options to the script :

# Colors for echo
NC='\033[0m'
YELLOW='\033[1;33m'

# Manual
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]
then
	echo "ABOUT"
	echo -e "  This script downloads a page containing current bitcoin price and saves\n  the new price in a file on a new line.\n"
    echo "PARAMETERS"
	echo "  -h, --help	Display the manual"
	echo "  --verbose, -v"	Verbose
fi

# Verbose option
if [[ "$*" == *"--verbose"* ]] || [[ "$*" == *"-v"* ]]
then
    echo -e "- Web page downloaded and saved in data/coingecko_btc.html"
	echo -e "- Bitcoin price saved in data/coingecko_btc.txt"
	echo -e "Current bitcoin price is: ${YELLOW}\$$bitcoin${NC}"
fi
