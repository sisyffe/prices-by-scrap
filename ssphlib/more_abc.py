"""
Other abstract classes that there isn't in python's stdlib
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

__all__ = ["SupportsGetitem", "SupportsGetitemAndSized"]


@runtime_checkable
class SupportsGetitem(Protocol):
    """An ABC with one abstract method __getitem__."""
    __slots__ = ()

    @abstractmethod
    def __getitem__(self):
        pass


@runtime_checkable
class SupportsGetitemAndSized(Protocol):
    """An ABC with two abstract method __getitem__ and __len__."""
    __slots__ = ()

    @abstractmethod
    def __getitem__(self):
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass
