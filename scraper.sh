#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# Downloading
curl -s https://www.coingecko.com/en/coins/bitcoin > "$parent_path/data/webpage.html"

# Getting value from HTML
bitcoin=$(cat $parent_path/data/webpage.html |  grep -o -P '(?<=\$).*(?=</span></span>)' | head -1)

# Saving value into a file
echo "$(date +'%Y-%m-%d %H:%M:%S')|$bitcoin" >> $parent_path/data/bitcoin-history.txt


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
    echo -e "- Web page downloaded and saved in data/webpage.html"
	echo -e "- Bitcoin price saved in data/bitcoin-history.txt"
	echo -e "Current bitcoin price is: ${YELLOW}\$$bitcoin${NC}"
fi