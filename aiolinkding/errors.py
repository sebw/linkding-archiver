"""Define package exceptions."""


class LinkDingError(Exception):
    """Define a base exception."""

    pass


class InvalidServerVersionError(LinkDingError):
    """Define an error related to an invalid server version."""

    pass


class InvalidTokenError(LinkDingError):
    """Define an error related to an invalid API token."""

    pass


class RequestError(LinkDingError):
    """An error related to invalid requests."""

    pass


class UnknownEndpointError(RequestError):
    """An error related to an unknown endpoint."""

    pass
