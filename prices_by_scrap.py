try:
    import selenium as _
except ImportError:
    import sys

    print("Selenium not installed. Please install it:")
    print(f"\tpip{str(ver) if (ver := sys.version_info.major) >= 3 else ''} install selenium")
    sys.exit(1)

import sys
import datetime as dt
from typing import List, Union

from ssphlib.log import exit_error, LogLevels

from src.initialize import initialize
from src.scrap import process_website
from src.calculate import calculate
from src.summary import summary
import settings as global_settings


date = dt.datetime.now().strftime("%H:%m:%S.%f")
if sys.version_info.major < 3:
    print("\x1b[3m\x1b[33m[WARNING]\x1b[0m: \x1b[1m"
          "Using this app in python 2 is highly not recommended. You can have crashes.\x1b[0m",
          file=sys.stderr)
elif sys.version_info.major >= 3 and sys.version_info.minor < 8:
    print("\x1b[3m\x1b[93m[WARNING]\x1b[0m: \x1b[1m"
          "This app is designed for python 3.8 or greater. Use python3.8 to be more reliable.\x1b[0m",
          file=sys.stderr)
del date


def scrap_help() -> None:
    print("Usage: ")
    print(f"\t{global_settings.PYTHON_EXECUTABLE} prices_by_scrap.py [arguments]\n")
    print(f"Example:")
    print(f"\t{global_settings.PYTHON_EXECUTABLE} prices_by_scrap.py -c Frankreich -c Deutschland -f result -s "
          f"2020-01-01 -l WARNING --no-summary\n")
    print(f"\tScrap the website for France (=Frankreich) and Germany (=Deutschland), save the result files in a folder"
          f"\n\tnamed \"result\", start on 1st of January 2020, show only warning and error messages and do not make a"
          f"\n\tsummary at the end.\n")
    print(f"Warning: ")
    print(f"\tCountries names must be in Germain. Tags -s and -e include the date you gave. The output folder will be"
          f"\n\tcreated. There could be duplicates in the prices result file if there is already the data. Changing"
          f"\n\tthe date format may crash the program. Duplicating a tag in the arguments with overwrite the"
          f"\n\tprevious one except for -c.\n")
    print(f"Arguments:")
    print(f"\t-c [Country] -> Country to scrap. You must to specify at least one.")
    print(f"\t-p [Prices output file = prices.csv]")
    print(f"\t-a [Average output file = average.csv]")
    print(f"\t-f [Output folders = .] -> Output folder")
    print(f"\t-s [Start date = 4 days ago if output not created] -> Date to start scrapping (included)")
    print(f"\t-e [End date = today] -> Date to end scrapping (included)")
    print(f"\t-l [Logging level (INFO, WARNING...) = INFO] -> Filter of log")
    print(f"\t-d [Date format = %Y-%m-%d (yyyy-mm-dd)] -> Date format everywhere")
    print(f"\t-m [Month date format = %Y-%m (yyyy-mm)] -> Date format to represent a month")
    print(f"\t--exit -> If a country does not exists in a page, exit the program (Default is False).")
    print(f"\t--no-scrap -> Skip the scrapping of the website (Default is False).")
    print(f"\t--no-average -> Skip the calculating of the average (Default is False).")
    print(f"\t--no-summary -> Skip summary (Default is False).")
    print(f"If you are using date, your can pass \"today\" for today.")
    sys.exit(0)


def main(argv: Union[List[str], str]) -> None:
    if isinstance(argv, str):
        argv = argv.split(" ")
    elif not isinstance(argv, list):
        exit_error(LogLevels.CRITICAL, "No arguments provided (or not str or list)", 2)

    print("\t\x1b[4m\x1b[96m=> Initializing the program\x1b[0m")
    settings = initialize(argv)

    if not settings["no_scrap"]:
        if (settings["end_date"] - settings["start_date"]).days >= 0:
            print("\t\x1b[4m\x1b[96m=> Scrapping website\x1b[0m")
            process_website(settings)
        else:
            print("\x1b[91m\x1b[1m\x1b[3m\t=> No page to scrap (data is up to date or "
                  "the end date happens before the start date)\x1b[0m")

    if not settings["no_average"]:
        print("\t\x1b[4m\x1b[96m=> Calculating average\x1b[0m")
        calculate(settings)

    if not settings["no_summary"]:
        print("\t\x1b[4m\x1b[96m=> Summary\x1b[0m")
        summary(settings)


if __name__ == "__main__":
    if "help" in " ".join(sys.argv) or len(sys.argv) < 2:
        scrap_help()
    main(argv=sys.argv[1:])
