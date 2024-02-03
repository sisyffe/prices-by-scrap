# prices-by-scrap
Small script to retrieve the local marginal price per hour for any country, at any time.
It uses a webdriver to get the infos on the `regelleistung.net` website.

## Prerequisites
```sh
pip3 install selenium
```
## Running
Run with custom arguments:
```sh
python3 runme.py
```
Simple run:
```sh
python3 prices_by_scrap.py -c Frankreich -l INFO
```
## Get help
```sh
python3 prices_by_scrap.py --help
```

## runme.py
This file is **meant to be changed by the user**. By default, it scraps for France and save the data in a folder named `result`.

## settings.py
You can also modify this file for **deep settings changes**.
However it is not recommended because you may confuse the program if not done properly.

## Web browser
This program is tested on firefox, but you can change to chrome if you want. Good luck!
