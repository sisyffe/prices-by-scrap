import datetime as dt
from pickle import dump
from time import time
from typing import Any, Dict, List, Tuple

from ssphlib.log import log, LogLevels
from ssphlib.utilities import decompose

from src.initialize import date_strptime
import settings as global_settings


def calculate(settings: Dict[str, Any]):

    start_calculate_time = time()
    _head = None

    def get_lines():
        nonlocal _head

        with open(settings["prices_output_file"], "r") as in_file:
            _head = in_file.readline()
            line = in_file.readline()
            while line != "":
                yield line.strip().split(global_settings.CSV_SEP)
                line = in_file.readline()

    def get_month(date_: dt.date) -> str:
        return date_.strftime(settings["month_date_format"])

    # Calculate the price for a day for each country (sum)
    data_day: Dict[str, Dict[dt.date, float]] = {}
    for date, country, _, value in get_lines():
        if country not in settings["countries"]:
            continue
        date = date_strptime(date, settings["date_format"])

        data_day.setdefault(country, {})
        data_day[country].setdefault(date, 0)
        data_day[country][date] += float(value)

    # Get the current month
    data_current_month: Dict[str, Dict[str, str]] = {}
    td = global_settings.TODAY
    for country, days in data_day.items():
        data_current_month.setdefault(country, {})
        for day, value in days.items():
            if day.year != td.year or day.month != td.month:
                continue
            value = value / global_settings.PRICE_DIVIDER
            data_current_month[country][day.strftime(settings["date_format"])] = \
                str(round(value, global_settings.ROUND_VALUE))

    # Sort by month
    data_month: Dict[str, Dict[str, List[float]]] = {}
    for country, days in data_day.items():
        data_month.setdefault(country, {})
        for day, value in days.items():
            month = get_month(day)
            data_month[country].setdefault(month, [])
            data_month[country][month].append(value / global_settings.PRICE_DIVIDER)

    # Mean of the month
    result: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
    for country, months in data_month.items():
        result.setdefault(country, {})
        for month, values in months.items():
            result[country][month] = (
                round(sum(values) / len(values), global_settings.ROUND_VALUE),
                round(min(values), global_settings.ROUND_VALUE),
                round(max(values), global_settings.ROUND_VALUE)
            )

    with open(global_settings.cache_file, "wb") as f:
        dump((result, data_current_month), f)

    # Save the result
    with open(settings["average_output_file"], "w") as f:
        f.write(global_settings.AVERAGE_CSV_HEAD)
        for country, months in result.items():
            for month, (value_mean, value_min, value_max) in months.items():
                line_data = (country, month, str(value_mean), str(value_min), str(value_max))
                f.write("\n" + global_settings.CSV_SEP.join(line_data))

    end_calculate_time = time()
    time_took = round((end_calculate_time - start_calculate_time) * 1000000)
    seconds, miliseconds, microseconds = decompose(time_took, (1000000, 1000))
    log(LogLevels.INFO,
        f"Calculating took {seconds} seconds, {miliseconds} miliseconds and {microseconds} microseconds.")
