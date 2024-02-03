"""
Various utilities for the library or you
"""

from functools import reduce, wraps
import operator
from typing import Any, Callable, Iterable, List, Tuple, Union

from .error import SSPHLIBDoesNotExistsError, SSPHLIBUnexpectedError
from .more_abc import SupportsGetitemAndSized

__all__ = ["match_letters", "make_int", "make_list", "t_apply", "duplicate", "get_sign", "unzip_index", "decompose",
           "chain_funcs"]


def match_letters(text: str, letters: str) -> bool:
    """
    Make sure a string (`text`) is composed only by certain letters (`letters`)
    :param text: The text to check on
    :param letters: A string of every char possible
    :return: Whether the text is composed by the letters
    """
    return all(char in letters for char in text)


def make_int(function: Callable):
    """
    Decorator to make the output of a function ints instead of floats (in a sequence or just the return)
    :param function: The function to wrap
    :return: The wrapper function
    """
    @wraps(function)
    def wrapper(*a, **kw):
        result = function(*a, **kw)
        if isinstance(result, tuple):
            return tuple(map(lambda f: round(f), result))
        elif isinstance(result, float):
            return round(result)
        else:
            raise SSPHLIBUnexpectedError("Result in not a tuple and not a float")

    return wrapper


def make_list(generator: Callable):
    """
    Decorator to execute a generator on its instantiation and return its result.
    Works only for simple generators and not double-way complex generators.
    Not meant to be used on list comprehension.
    :param generator: The generator-function
    :return: The wrapper function
    """
    @wraps(generator)
    def wrapper(*a, **kw):
        gen = generator(*a, **kw)
        return list(gen)

    return wrapper


def t_apply(t1: tuple, *ts: tuple, ope: Union[Callable, str] = operator.add) -> tuple:
    """
    Apply an operator/function on two tuples or more
    :param t1: The first compulsory tuple
    :param ts: Other tuples
    :param ope: The function to perform
    :return: The result tuple
    """
    # Check ope (str=>getattr(operator, ope), Callable=>ope)
    if isinstance(ope, str):
        if not hasattr(operator, ope):
            raise SSPHLIBDoesNotExistsError(f"Bad ope name '{ope}' for module operator")
        ope = getattr(operator, ope)

    # Apply
    def generator():
        for values in zip(t1, *ts):
            yield reduce(ope, values)

    return tuple(generator())


def duplicate(value: Any, duplicates: int) -> Tuple[Any, ...]:
    """
    Just return `duplicates` times `value`
    :param value: The value to duplicate
    :param duplicates: The number of duplicates
    :return: All duplicates
    """
    return tuple(value for _ in range(duplicates))


def get_sign(num: float) -> int:
    """
    Get the sign of a number (neg: -1, 0: 0, pos: 1)
    :param num: The number
    :return: The sign (neg: -1, 0: 0, pos: 1)
    """
    if num == 0:
        return 0
    return int(num / abs(num))


def unzip_index(iterable: Iterable[SupportsGetitemAndSized], index: int) -> List[Any]:
    """
    Returns a list of the `index`-th element of each tuple/list/index-able in a sequence
    Example: zip_index([(1, 2, 3), (4, 5, 6), (7, 8, 9)], 1) -> [2, 5, 8]
    Warning: loops over `iterable` and destroys it if it is a generator
    :param iterable: The iterable that contains the index-able objects
    :param index: The index to take the values
    :return: Thew list of values
    """
    @make_list
    def generator():
        for elem in iterable:
            if index >= len(elem):
                raise SSPHLIBUnexpectedError(f"One element is too short ({len(elem)} elements)")
            yield elem[index]

    return generator()


def decompose(number: int, dividers: Iterable) -> List[int]:
    """
    Decompose a number into pieces with dividers.
    Example: `decompose(183894, (86400, 3600, 60)) = [2, 3, 4, 5]`
              => 183894 seconds = 2 days (86400 seconds), 3 hours (3600 seconds), 4 minutes and 5 seconds
    It returns the last remainder too (len(dividers) + 1)
    :param number: The number to decompose
    :param dividers: All dividers
    :return: A list of the decomposed number
    """
    @make_list
    def generator():
        current, remainder = number, 0
        for div in dividers:
            quotient, remainder = divmod(current, div)
            current = remainder
            yield quotient
        yield remainder
    return generator()


def chain_funcs(functions: Iterable[Callable], initial_value: Any) -> Any:
    """
    Execute multiple functions after each other:
    chain_funcs([a, b, c], val) = c(b(a(val)))
    :param functions: Iterable containing every function to call
    :param initial_value: The initial value to process
    :return: The return of the last function
    """
    last = initial_value
    for func in functions:
        last = func(last)
    return last
