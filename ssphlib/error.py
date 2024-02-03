"""
Errors for this library
"""

__all__ = ["SSPHLIBError", "SSPHLIBBadLiteralError", "SSPHLIBDoesNotExistsError", "SSPHLIBInstantiatedError",
           "SSPHLIBUnexpectedError", "SSPHLIBWrongArgumentError"]


class SSPHLIBError(Exception):
    """
    Base error
    """
    pass


class SSPHLIBBadLiteralError(SSPHLIBError):
    """
    When you have a string literal parameter, and it's not respected
    """
    pass


class SSPHLIBDoesNotExistsError(SSPHLIBError):
    """
    When an identifier / name does not exist in a database
    """
    pass


class SSPHLIBInstantiatedError(SSPHLIBError):
    """
    When a class meant to not be instantiated is instantiated
    """
    pass


class SSPHLIBUnexpectedError(SSPHLIBError):
    """
    Kinda like base RuntimeError
    """
    pass


class SSPHLIBWrongArgumentError(SSPHLIBError):
    """
    When a wrong/misunderstood argument makes a function raise an error
    """
    pass
