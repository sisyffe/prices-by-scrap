import sys
import datetime as dt
from time import sleep, time
from typing import Any, Dict, List, Optional, Set

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from ssphlib.log import log, LogLevels
from ssphlib.utilities import decompose

from src import xpaths
import settings as global_settings

do_exit: bool = False
err_count: int = 0


def try_find(wd: webdriver, path: str) -> Optional[str]:
    count = 0
    while count <= global_settings.MAX_TRIES:
        try:
            count += 1
            result = wd.find_element(by=By.XPATH, value=path).text
        except common.exceptions.NoSuchElementException:
            sleep(global_settings.WAIT_TRIES)
        else:
            return result
    return None


def try_find_one(wd: webdriver, path: str) -> Optional[List[str]]:
    result = []
    count, errors = 1, 0
    while True:
        try:
            result.append(wd.find_element(by=By.XPATH, value=path.format(count)).text)
            count += 1
        except common.exceptions.NoSuchElementException:
            if count > 1:
                return result
            if errors >= global_settings.MAX_TRIES - 1:
                return None
            if count == 1:
                errors += 1
                sleep(global_settings.WAIT_TRIES)


def get_table_xpath(wd: webdriver) -> str:
    if try_find(wd, xpaths.TABLE) is not None:
        return xpaths.TABLE
    elif try_find(wd, xpaths.TABLE_BIS) is not None:
        return xpaths.TABLE_BIS
    else:
        return ""


def get_data(
        wd: webdriver.Firefox,
        countries: Set[str],
        current_date: dt.date,
        date_format: str,
        exit_if_error: bool,
) -> Dict[str, Dict[str, str]]:
    global do_exit, err_count

    table_xpath = get_table_xpath(wd)
    head = try_find_one(wd, xpaths.head_columns(table_xpath))
    all_countries = try_find_one(wd, xpaths.countries(table_xpath))

    result: Dict[str, Dict[str, str]] = {}
    for country in countries:
        if country not in all_countries:
            print("\r", end="")
            log(LogLevels.ERROR, f"Country {country!r} not found on the website "
                                 f"date {dt.date.strftime(current_date, date_format)}. "
                                 f"{'Exit' if exit_if_error else 'Skip'}")
            err_count += 1
            if exit_if_error:
                do_exit = True
                break
            continue

        result[country] = {}
        line = 1 + all_countries.index(country)

        for column in range(2, len(head) + 2):
            result[country][head[column - 2]] = wd.find_element(
                by=By.XPATH, value=xpaths.value(table_xpath).format(line=line, column=column)).text

    return result


def get_result(result, current_date, date_format: str) -> str:
    str_result = ""
    for country in result.keys():
        for name in result[country].keys():
            date = dt.date.strftime(current_date, date_format)
            value = result[country][name].replace(".", "").replace(",", ".")
            str_result += "\n" + global_settings.CSV_SEP.join((str(date), str(country), str(name), str(value)))
    return str_result


def scrap_page(
        url: str,
        wd: webdriver.Firefox,
        current_date: dt.date,
        date_format: str,
        countries: Set[str],
        exit_if_error: bool,
        output_file: str
) -> None:
    global do_exit
    do_exit = False

    print("\r", "\x1b[1m\x1b[3m=> Current date: ", dt.date.strftime(current_date, date_format),
          "\x1b[0m", end="", sep="")
    sys.stdout.flush()
    wd.get(url.format(date=dt.date.strftime(current_date, global_settings.WEBSITE_DATE_FORMAT)))

    result = get_data(wd, countries, current_date, date_format, exit_if_error)
    with open(output_file, "a") as f:
        f.write(get_result(result, current_date, date_format))


def scrap(
        url: str,
        wd: webdriver.Firefox,
        start_date: dt.date,
        end_date: dt.date,
        date_format: str,
        countries: Set[str],
        exit_if_error: bool,
        output_file: str
) -> None:
    start_scrap_time = time()

    difference = end_date - start_date
    for gap in range(difference.days + 1):
        current_date = start_date + dt.timedelta(gap)
        scrap_page(url, wd, current_date, date_format, countries, exit_if_error, output_file)
        if do_exit:
            break

    end_scrap_time = time()
    time_took = round(end_scrap_time - start_scrap_time)
    minutes, seconds = decompose(time_took, (60,))
    print("\r", " " * 25, "\r", end="")
    log(LogLevels.INFO, f"Scrapping took {minutes} minutes and {seconds} seconds.")


def process_website(settings: Dict[str, Any]) -> None:
    # Initialize web driver
    wd = None
    try:
        # noinspection PyUnresolvedReferences
        wd = webdriver.Firefox(
            service=webdriver.firefox.service.Service(settings["driver_path"]),
            options=webdriver.FirefoxOptions()
        )
    except common.exceptions.WebDriverException as exc:
        log(LogLevels.CRITICAL, "Webdriver can't be initialized. \nIf you don't have Firefox, "
                                "please install it (https://www.mozilla.org/en-US/firefox/new/).")
        log(LogLevels.CRITICAL, f"{type(exc).__name__}: {str(exc)}")
    else:
        # Scrap the website
        scrap(global_settings.URL, wd, settings["start_date"], settings["end_date"], settings["date_format"],
              settings["countries"], settings["exit_if_error"], settings["prices_output_file"])
        if err_count > 0:
            print(f"\x1b[1m\x1b[31m\t=> {err_count} error(s) happened\x1b[0m")
    finally:
        # Close the driver
        if wd is not None:
            wd.close()
