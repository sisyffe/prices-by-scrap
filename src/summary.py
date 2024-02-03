import os
from pickle import load
from typing import Any, Dict, List, Literal, Tuple, Union

from ssphlib.log import log, LogLevels
from ssphlib.utilities import duplicate, unzip_index

from src.initialize import date_strptime
import settings as global_settings

AVERAGE_CSV_HEAD = global_settings.AVERAGE_CSV_HEAD.split(global_settings.CSV_SEP)
PRICES_CSV_HEAD = global_settings.PRICES_CSV_HEAD.split(global_settings.CSV_SEP)

columns: List[Tuple[str, int]]


def print_sep(place: Literal["top", "middle", "bottom"] = "middle"):
    if place == "top":
        print("┌", "┬".join(("─" * (n + 2) for n in unzip_index(columns, 1))), "┐", sep="")  # noqa
    elif place == "middle":
        print("├", "┼".join(("─" * (n + 2) for n in unzip_index(columns, 1))), "┤", sep="")  # noqa
    elif place == "bottom":
        print("└", "┴".join(("─" * (n + 2) for n in unzip_index(columns, 1))), "┘", sep="")  # noqa


def print_title():
    print_line(unzip_index(columns, 0), "left")  # noqa
    print_sep("middle")


def print_line(values: Union[List[str], Any], side: Literal["left", "right"] = "right"):
    values = [(" " * (columns[i][1] - len(t)) if side == "right" else "") + t +  # noqa
              (" " * (columns[i][1] - len(t)) if side == "left" else "") for i, t in enumerate(values)]  # noqa
    print("│ ", " │ ".join(values), " │", sep="")


def summary_total(settings: Dict[str, Any], values: Dict[str, Tuple[float, float, float]]):
    global columns

    # Determinate width of columns
    max_month = 0
    max_values = dict(zip(AVERAGE_CSV_HEAD[2:], duplicate(0, 3)))
    for month, nums in values.items():
        max_month = max(max_month, len(month))
        for name, val in zip(AVERAGE_CSV_HEAD[2:], nums):
            max_values[name] = max(max_values[name], len(str(val)))
    max_month = max(max_month, len(AVERAGE_CSV_HEAD[1]))
    max_values = {k: max(v, len(AVERAGE_CSV_HEAD[AVERAGE_CSV_HEAD.index(k)])) for k, v in max_values.items()}
    columns = [(AVERAGE_CSV_HEAD[1], max_month), *max_values.items()]

    # Print table
    print_sep("top")
    print_title()
    last_year = None
    for month, (value_mean, value_min, value_max) in values.items():
        date = date_strptime(month, settings["month_date_format"])
        if last_year != date.year and last_year is not None:
            print_sep("middle")
            print_title()
        last_year = date.year
        print_line((month, str(value_mean), str(value_min), str(value_max)))
    print_sep("bottom")


def summary_month(values: Dict[str, str]):
    global columns

    # Determinate width of columns
    max_day = 0
    max_value = 0
    for month, value in values.items():
        max_day = max(max_day, len(month))
        max_value = max(max_value, len(value))

    max_day = max(max_day, len(PRICES_CSV_HEAD[0]))
    max_value = max(max_value, len(PRICES_CSV_HEAD[3] + " per hour"))
    columns = [(PRICES_CSV_HEAD[0], max_day), (PRICES_CSV_HEAD[3] + " per hour", max_value)]

    # Print table
    print_sep("top")
    print_title()
    for month, value in values.items():
        print_line((month, value))
    print_sep("bottom")


def summary(settings: Dict[str, Any]) -> None:
    if not os.path.exists(global_settings.cache_file):
        log(LogLevels.ERROR, f"Cannot make a summary: cache file ({global_settings.cache_file}) not found")
        return

    # Load cache
    with open(global_settings.cache_file, "rb") as f:
        raw_data = load(f)
        data: Dict[str, Dict[str, Tuple[float, float, float]]] = raw_data[0]
        data_current_month: Dict[str, Dict[str, str]] = raw_data[1]
    if global_settings.DELETE_CACHE:
        os.remove(global_settings.cache_file)

    if len(data) == 0:
        print("Nothing to show")
    # Print data
    for (country_data, values_data), (country_month, values_month) in zip(data.items(), data_current_month.items()):
        assert country_data == country_month
        country = country_data
        if country not in settings["countries"]:
            continue
        print(f"\t\t\x1b[1m\x1b[4m\x1b[94m{country}\x1b[0m")

        print(f"\t\x1b[1m\x1b[4m\x1b[94mSummary of all the averages per months ({country})\x1b[0m")
        summary_total(settings, values_data)
        print(f"\t\x1b[1m\x1b[4m\x1b[94mSummary of the current month ({country})\x1b[0m")
        summary_month(values_month)
