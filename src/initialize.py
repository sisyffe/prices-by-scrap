import os
import sys

import datetime as dt
from typing import Any, Callable, Dict, Union

from ssphlib.log import log, exit_error, exit_if, LogLevels, set_log_format
import settings as global_settings

argv: str
settings: Dict[str, Any]

argument, next_argument = "", ""


def date_strptime(date_string: str, fmt: str) -> dt.date:
    date_obj = dt.datetime.strptime(date_string, fmt)
    return dt.date(year=date_obj.year, month=date_obj.month, day=date_obj.day)


class ArgsParser:
    __slots__ = []

    @classmethod
    def additive(cls, name: str, func: Union[Callable, None] = None) -> None:
        if func is None:
            func = lambda var: var  # noqa
        if next_argument is None:
            log(LogLevels.WARNING, f"Nothing after tag \"{argument}\". Ignoring. Default is {settings[name]}")
        else:
            assert isinstance(settings[name], set)
            settings[name].add(func(next_argument))

    @classmethod
    def classic(cls, name: str, func: Union[Callable, None] = None) -> None:
        if func is None:
            func = lambda var: var  # noqa
        if next_argument is None:
            log(LogLevels.WARNING, f"Nothing after tag \"{argument}\". Ignoring. Default is {settings[name]}")
        else:
            settings[name] = func(next_argument)

    @classmethod
    def date(cls, name: str):
        if next_argument is None:
            log(LogLevels.WARNING, f"Nothing after tag \"{argument}\". Ignoring. Default is {settings[name]}")
        elif next_argument == global_settings.TODAY_TOKEN:
            settings[name] = global_settings.TODAY
        else:
            try:
                settings[name] = date_strptime(next_argument, settings["date_format"])
            except ValueError:
                exit_error(LogLevels.ERROR, f"Date {next_argument!r} ({name.replace('_', ' ')}) doesn't match "
                                            f"format {settings['date_format']!r}", 5)


class InitializeSteps:
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Cannot instantiate this class")

    @classmethod
    def logging_and_dates(cls) -> None:
        global argument, next_argument
        set_log_format("\x1b[3m{color}[{level}]\x1b[0m: \x1b[1m{message}\x1b[0m\n")

        # Log level
        if "-l" in argv:
            str_level = None
            try:
                str_level = argv[argv.index("-l") + 1]
                settings["log_level"] = getattr(LogLevels, str_level)
            except IndexError:
                log(LogLevels.WARNING, "Nothing after tag \"-l\". Ignoring")
            except (AttributeError, SyntaxError):
                log(LogLevels.WARNING, f"Level after tag \"-l\" ({str_level!s}) is not a level. "
                                       f"Default is {LogLevels.get_with_number(LogLevels.current)[0]}")
        LogLevels.current = settings["log_level"]

        # Date formats (-d, -m)
        for argument in global_settings.DATE_FORMAT_TAGS:
            if argument not in argv:
                continue
            index = argv.index(argument)
            next_argument = argv[index + 1] if index + 1 < len(argv) else None
            ArgsParser.classic(global_settings.TAGS_CORRESPONDENCE[argument])

    @classmethod
    def settings(cls) -> None:
        global argument, next_argument

        index = 0
        while index < len(argv):
            argument = argv[index]
            next_argument = argv[index + 1] if index + 1 < len(argv) else None
            log(LogLevels.DEBUG, f"{argument=} {next_argument=}")

            if argument == "":
                index += 1
                continue
            elif argument in global_settings.ADDITIVE_TAGS:
                ArgsParser.additive(global_settings.TAGS_CORRESPONDENCE[argument])
            elif argument in global_settings.FILE_TAGS:
                ArgsParser.classic(global_settings.TAGS_CORRESPONDENCE[argument],
                                   lambda var: os.path.expandvars(os.path.expanduser(var)))
            elif argument in global_settings.CLASSIC_TAGS:
                ArgsParser.classic(global_settings.TAGS_CORRESPONDENCE[argument])
            elif argument in global_settings.DATE_TAGS:
                ArgsParser.date(global_settings.TAGS_CORRESPONDENCE[argument])
            elif argument == "--exit":
                settings["exit_if_error"] = True
            elif argument.startswith("--no-"):
                settings[f"no_{argument[len('--no-'):]}"] = True
            elif argument not in global_settings.ALL_TAGS:
                exit_error(LogLevels.ERROR, f"Invalid arguments format: perhaps you forgot the value after a tag "
                                            f"(detected value: \"{next_argument}\") or the tag is invalid "
                                            f"(detected tag: \"{argument}\")", 4)

            index += 2 if argument in global_settings.ALL_TAGS else 1

        # Update result_file
        settings["prices_output_file"] = os.path.join(settings["output_folder"], settings["prices_output_file"])
        settings["average_output_file"] = os.path.join(settings["output_folder"], settings["average_output_file"])
        global_settings.cache_file = os.path.join(settings["output_folder"], global_settings.cache_file)

    @classmethod
    def directories(cls) -> None:
        def try_create(function: Callable, error: str) -> None:
            try:
                function()
            except RuntimeError:
                exit_error(LogLevels.CRITICAL, error + " Exit.")

        if not os.path.exists(settings["output_folder"]):
            try_create(lambda: os.mkdir(settings["output_folder"]),
                       f"Output folder {settings['output_folder']!r} cannot be created.")

        def prices_func():
            with open(settings["prices_output_file"], "w") as f:
                f.write(global_settings.PRICES_CSV_HEAD)

        if not os.path.exists(settings["prices_output_file"]):
            try_create(prices_func, f"File {settings['prices_output_file']!r} cannot be created.")

    @classmethod
    def start_date_from_file(cls) -> None:
        def dates_of(io):
            line = io.readline()  # Skip first line (head)
            while line != "":
                line = io.readline()
                if not line:
                    break
                split = line.split(global_settings.CSV_SEP)
                try:
                    yield date_strptime(split[0], settings["date_format"]), split[1]
                except ValueError:
                    continue

        if "-s" not in argv:  # Argument has not been specified and the file exists: take the newest from the file
            with open(settings["prices_output_file"], "r") as f:
                max_date = None
                for current_date, _country in dates_of(f):
                    if max_date is None:
                        max_date = current_date
                    if current_date > max_date:
                        max_date = current_date
            if max_date is None:
                log(LogLevels.WARNING,
                    f"Output file ({settings['prices_output_file']}) is empty: cannot determine the start date. "
                    f"Default is {dt.date.strftime(settings['start_date'], settings['date_format'])}.")
            else:
                settings["start_date"] = max_date + dt.timedelta(days=1)

    @classmethod
    def driver_path(cls) -> None:
        # Determine driver path
        extension, platform = "", "unknown"
        if sys.platform.startswith("darwin"):
            platform = "darwin"
        elif sys.platform.startswith("win"):
            platform = "win"
            extension = ".exe"
        elif sys.platform.startswith("linux"):
            platform = "linux"
        else:
            exit_error(LogLevels.CRITICAL, f"Platform {sys.platform!r} unsupported. Exit.", 2)

        settings["driver_path"] = global_settings.DRIVER_NAME_FORMAT.format(
            version=global_settings.DRIVER_VERSION,
            platform=platform,
            architecture=global_settings.PROCESSOR,
            extension=extension
        )


def initialize(args: list) -> Dict[str, Any]:
    global argv, settings
    argv, settings = args, global_settings.DEFAULT_SETTINGS.copy()

    InitializeSteps.logging_and_dates()  # Create a basic config of logging
    InitializeSteps.settings()  # Set variables with arguments
    InitializeSteps.directories()  # Set result folder
    InitializeSteps.start_date_from_file()  # Set start date with the last date in the result file
    InitializeSteps.driver_path()  # Set the driver path depending on the platform

    exit_if(len(settings["countries"]) == 0, LogLevels.ERROR,
            "No country specified. Please specify one with the command line arguments (see help for more info).")

    log(LogLevels.INFO, f"\x1b[0m\x1b[3mStart date: \x1b[0m\x1b[33m"
                        f"{dt.date.strftime(settings['start_date'], settings['date_format'])}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mEnd date: \x1b[0m\x1b[33m"
                        f"{dt.date.strftime(settings['end_date'], settings['date_format'])}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mCountries: \x1b[0m\x1b[33m{', '.join(settings['countries'])}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mPrices result file: \x1b[0m\x1b[33m{settings['prices_output_file']}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mAverage result file: \x1b[0m\x1b[33m{settings['average_output_file']}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mExit if error: \x1b[0m\x1b[33m{'yes' if settings['exit_if_error'] else 'no'}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mScrap website: \x1b[0m\x1b[33m{'yes' if not settings['no_scrap'] else 'no'}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mCalculate average: \x1b[0m\x1b[33m"
                        f"{'yes' if not settings['no_average'] else 'no'}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mSummarize: \x1b[0m\x1b[33m{'yes' if not settings['no_summary'] else 'no'}")
    log(LogLevels.INFO, f"\x1b[0m\x1b[3mDriver: \x1b[0m\x1b[33m{settings['driver_path']}")

    settings.pop("output_folder")
    return settings
