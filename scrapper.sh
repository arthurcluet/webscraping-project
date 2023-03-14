#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# Downloading
curl -s https://www.coingecko.com/en/coins/bitcoin > "$parent_path/data/webpage.html"

# Getting value from HTML
bitcoin=$(cat $parent_path/data/webpage.html |  grep -o -P '(?<=\$).*(?=</span></span>)' | head -1)

# Saving value into a file
echo "$(date +'%Y-%m-%d %H:%M:%S')|$bitcoin" >> $parent_path/data/bitcoin-history.txt