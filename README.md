# prices-by-scrap
Small script to retrieve the local marginal price per hour

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

When you run with `runme.py`, result files are stored in `result/prices.csv` and `result/average.csv`.
