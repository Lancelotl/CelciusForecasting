class HttpError(Exception):
    """Couldn't access the page"""

    pass


class BadResponse(Exception):
    """Did not find forecasts in the page"""

    pass


class UnexpectedFormat(Exception):
    """Individual forecast did not match expected format"""

    pass


class OutOfRange(Exception):
    """Did not find the desired individual forecast"""

    pass


class MissingAPIKey(Exception):
    """Did not find the API keys in the environment variables"""

    pass
