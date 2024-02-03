import sys
import datetime as dt
from typing import Literal

from ssphlib.log import LogLevels

# Website
# https://www.regelleistung.net/apps/datacenter/tenders/?productTypes=PRL&markets=BALANCING_CAPACITY&date=2022-12-31&tenderTab=PRL$CAPACITY$1

# Constants
PYTHON_EXECUTABLE = f"python{str(ver) if (ver := sys.version_info.major) >= 3 else ''}"
URL = "https://www.regelleistung.net/apps/datacenter/tenders/" + \
      "?productTypes=PRL&markets=BALANCING_CAPACITY&date={date}&tenderTab=PRL$CAPACITY$1"
TODAY = dt.date.today()
# Tags
TAGS_CORRESPONDENCE = {"-c": "countries", "-p": "prices_output_file", "-a": "average_output_file",
                       "-f": "output_folder", "-s": "start_date", "-e": "end_date", "-l": "log_level",
                       "-d": "date_format", "-m": "month_date_format"}
ADDITIVE_TAGS = ("-c",)
FILE_TAGS = ("-p", "-a")
CLASSIC_TAGS = ("-f",)
DATE_TAGS = ("-s", "-e")
DATE_FORMAT_TAGS = ("-d", "-m")
PREPROCESSED_TAGS = ("-l", *DATE_FORMAT_TAGS)
ALL_TAGS = (*ADDITIVE_TAGS, *FILE_TAGS, *CLASSIC_TAGS, *DATE_TAGS, *PREPROCESSED_TAGS)

# Settings changeable by command line arguments (default values)
DEFAULT_SETTINGS = {
    "countries": set(),
    "prices_output_file": "prices.csv",
    "average_output_file": "average.csv",
    "output_folder": ".",
    "start_date": TODAY - dt.timedelta(days=4 - 1),
    "end_date": TODAY,
    "log_level": LogLevels.INFO,
    "date_format": "%Y-%m-%d",
    "month_date_format": "%Y-%m",
    "exit_if_error": False,
    "no_scrap": False,
    "no_average": False,
    "no_summary": False,
}

# Settings
# CSV
CSV_SEP = ";"
PRICES_CSV_HEAD = CSV_SEP.join(("Date", "Country", "Period", "Local marginal capacity price (euro/MW)"))
AVERAGE_CSV_HEAD = CSV_SEP.join(("Country", "Month", "Mean of the LMCP per hour (euro/MW)", "Min", "Max"))
# Driver
DRIVER_VERSION: str = "v0.34.0"
DRIVER_NAME_FORMAT = "drivers/geckodriver-{version}-{platform}-{architecture}{extension}"
PROCESSOR: Literal["x86", "x86-64", "arm64"] = "x86-64"
# Timeouts
TIMEOUT_TIME = 2
WAIT_TRIES = 0.1
MAX_TRIES = TIMEOUT_TIME / WAIT_TRIES
# Others
WEBSITE_DATE_FORMAT = "%Y-%m-%d"
TODAY_TOKEN = "today"
PRICE_DIVIDER = 24
ROUND_VALUE = 2
DELETE_CACHE = True

cache_file: str = "cache.pkl"
