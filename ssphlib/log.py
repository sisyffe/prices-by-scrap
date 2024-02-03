"""
In this file, there is everything you want for logging.
"""

import datetime
import inspect
import os
import string
import sys
import types
from typing import Callable, TextIO, Tuple, Union

from .error import SSPHLIBDoesNotExistsError, SSPHLIBInstantiatedError, SSPHLIBWrongArgumentError
from .utilities import match_letters

__all__ = ["LogLevels", "set_log_format", "log", "exit_error", "exit_if"]


_IGNORE_FUNCTIONS = ["exit_error", "exit_if"]
_DEFAULT_LOG_FORMAT = "\x1b[33m[{date}]\x1b[0m In '\x1b[95m{func}\x1b[0m' from \x1b[35m{file}\x1b[0m: "\
               "\n\x1b[3m{color}[{level}]\x1b[0m: \x1b[1m{message}\x1b[0m\n\n"

_log_format = _DEFAULT_LOG_FORMAT


class __LogLevelsMeta(type):
    ATTR_LEVELS = "_levels"
    ATTR_LOG_LEVEL = "_log_level"
    """
    Metaclass for LogLevels
    """
    def __getattr__(cls, item):
        if not cls.exists(item):
            raise AttributeError(repr(item))
        return getattr(cls, cls.ATTR_LEVELS)[item][0]

    @property
    def current(cls) -> int:
        return getattr(cls, cls.ATTR_LOG_LEVEL)

    @current.setter
    def current(cls, new_log_level: Union[int, str]):
        if not cls.exists(new_log_level):
            raise SSPHLIBDoesNotExistsError("'new_log_level' does not exists")
        if isinstance(new_log_level, int):
            setattr(cls, cls.ATTR_LOG_LEVEL, new_log_level)
        elif isinstance(new_log_level, str):
            setattr(cls, cls.ATTR_LOG_LEVEL, getattr(cls, cls.ATTR_LEVELS)[new_log_level][0])
        else:
            raise SSPHLIBWrongArgumentError(f"'new_log_level must be int or str, not {type(new_log_level).__name__}")

    def add_level(cls, level_name: str, level_number: int, color: str = ""):
        if level_name == "":
            raise SSPHLIBWrongArgumentError("'level_name' cannot be empty")
        elif not match_letters(level_name, string.ascii_uppercase):
            raise SSPHLIBWrongArgumentError("'level_name' must be composed of uppercase ascii letters")
        elif cls.exists(level_number):
            raise SSPHLIBWrongArgumentError("Level already exists (value)")
        elif cls.exists(level_name):
            raise SSPHLIBWrongArgumentError("Level already exists (name)")
        elif color[0] != '\x1b' or color[1] != '[' or color[-1] != 'm':
            raise SSPHLIBWrongArgumentError("'color' is not a ANSI color")

        getattr(cls, cls.ATTR_LEVELS)[level_name] = (level_number, color)

    def exists(cls, level: Union[int, str]) -> bool:
        if isinstance(level, int):
            return level in map(lambda v: v[0], getattr(cls, cls.ATTR_LEVELS).values())
        elif isinstance(level, str):
            return level in getattr(cls, cls.ATTR_LEVELS).keys()
        else:
            return False

    def get_with_number(cls, level_number: int) -> Tuple[str, int, str]:
        for name, v in getattr(cls, cls.ATTR_LEVELS).items():
            if v[0] == level_number:
                return str(name), int(v[0]), str(v[1])
        raise SSPHLIBDoesNotExistsError(f"level_number '{level_number}' does not exists")


class LogLevels(metaclass=__LogLevelsMeta):
    """
    Log levels manager: add, set, ...
    Starts with 5 different and you can add more
    """
    _levels = {
        "DEBUG": (10, "\x1b[36m"),
        "INFO": (20, "\x1b[32m"),
        "WARNING": (30, "\x1b[93m"),
        "ERROR": (40, "\x1b[31m"),
        "CRITICAL": (50, "\x1b[91m")
    }

    _log_level = 20

    def __new__(cls, *args, **kwargs):
        raise SSPHLIBInstantiatedError("Cannot create an instance of this class")


def set_log_format(new_log_format: str):
    """
    Change the log format. Pass empty string to bring back de default
    :param new_log_format: the new log format
    """
    global _log_format
    if new_log_format == "":
        _log_format = _DEFAULT_LOG_FORMAT
    else:
        _log_format = str(new_log_format)


def log(level: int, message: str, _code=None, *, file: TextIO = sys.stdout, ignore_log_functions: bool = True):
    """
    Log something. Does not print anything if `LogLevels.current is greater than `level`
    :param level: The log level. You should use `LogLevels.XYZ`
    :param message: The message to output. Can be anything
    :param _code: Dummy parameter to make this function compatible with exit_error
    :param file: The file to print the message. Default to the standard output
    :param ignore_log_functions: In the inspection for the caller function,
    ignore log function like `exit_error` if True
    """
    # Abort if level is too small
    if level < LogLevels.current:
        return

    # Get other info
    if not LogLevels.exists(level):
        raise SSPHLIBDoesNotExistsError(f"No such level {level}")
    level_name, _, color = LogLevels.get_with_number(level)

    if not hasattr(file, "write"):
        raise SSPHLIBWrongArgumentError("File must be writable")

    # Get callers module and name
    def get_callers_frame(current: Union[types.FrameType, None] = None) -> types.FrameType:
        if current is None:
            current = inspect.currentframe()
        return current.f_back

    def get_name(frame: types.FrameType) -> str:
        return frame.f_code.co_name

    ignore_functions = [inspect.currentframe().f_code.co_name]
    if ignore_log_functions:
        ignore_functions += _IGNORE_FUNCTIONS

    callers_frame = None
    while callers_frame is None or get_name(callers_frame) in ignore_functions:
        callers_frame = get_callers_frame(callers_frame)

    callers_name = get_name(callers_frame)
    callers_file = inspect.getsourcefile(callers_frame)
    callers_file = os.path.relpath(callers_file, os.getcwd())

    date = datetime.datetime.now().strftime("%H:%m:%S.%f")

    # Final write
    file.write(_log_format.format(date=date, func=callers_name, file=callers_file, color=color,
                                  level=level_name.upper(), message=message))


def exit_error(level: int, message: str, code: int = 1):
    """
    Logs something into stderr and the exits the program (sys.exit)
    :param level: Log level. Should be greater than or error
    :param message: The error message
    :param code: Exit code. Default to 1
    """
    log(level, message, file=sys.stderr)
    log(LogLevels.INFO, "Exiting the program because of an error", file=sys.stderr, ignore_log_functions=False)
    sys.exit(code)


def exit_if(value: Union[Callable, bool], level: int, message: str, code: int = 1):
    """
    Logs something into stderr and the exits the program (sys.exit)
    if the return value of `value` (if it's a function) or `value` evaluates to True
    :param value: The condition. If this is True or this returns True, the code is executed
    :param level: Log level. Should be greater than or error
    :param message: The error message
    :param code: Exit code. Default to 1
    """
    if hasattr(value, "__call__"):
        value = value()
    if bool(value):
        exit_error(level, message, code)
