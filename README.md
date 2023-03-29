
# Web Scraping with Git, Linux & Python

<a href="https://crypto.arthurcluet.dev" target="_blank">Working demo</a>

## Features

<img src="https://github.com/arthurcluet/webscraping-project/raw/master/demo.png" />

## About this project

### Web scraping

The purpose of this project is to perform web scraping only with a shell script. For this, I used the `curl` command to _retrieve the content of a web page_, then `grep`, `tail`, and `head` to _filter the content of the page_ and _retrieve only the price_ of the cryptocurrencies, and chose to _save the result directly to a file_, along with the date.

This "web scraping" part is done from the shell script [scraper.sh](https://github.com/arthurcluet/webscraping-project/blob/master/scraper.sh).

### Dashboard

The second part of the project is to display the retrieved data on a web dashboard created in Python with the Dash library.

This part is done with the python script [dashboard.py](https://github.com/arthurcluet/webscraping-project/blob/master/dashboard.py).


### Daily reports

The third part of this project is to produce daily reports everyday at 8pm, which must include the open and closing price, the evolution of the price, as well as the volatility. Using CRONs, a Python script is executed at 8pm and generates that daily report with prices since 8pm the previous day (since there is no open or close price with cryptocurrencies).

This part is done with the python script [report.py](https://github.com/arthurcluet/webscraping-project/blob/master/report.py).


## How it works

### Cron

I used cron jobs to have the scraping script retrieve the price of the cryptocurrencies every two minutes and create a report each day at 8pm. Command to use:
```bash
crontab -e
```
Lines to add to the list of cron jobs:
```
*/2 * * * * $PATH_TO_PROJECT/scraper.sh
0 20 * * * python3 $PATH_TO_PROJECT/report.py
```

### Dashboard server start

The dashboard part is still running in _debug mode_ but it can be started with:

```bash
python3 dashboard.py
```

_It currently starts under debug mode._
