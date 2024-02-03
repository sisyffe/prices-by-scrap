import sys
from prices_by_scrap import main as prices_by_scrap

ARGUMENTS = (
    "-c Frankreich "
    "-f result "
    "-p prices-france-since-2020.csv "
    "-a average-france-since-2020.csv "
    "-l INFO "
    "-e today"
)

prices_by_scrap([*ARGUMENTS.split(" "), *sys.argv[1:]])
