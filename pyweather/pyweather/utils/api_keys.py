import os
from ..exceptions import MissingAPIKey

def find_key(key_name):
    """Attempts to find the following API key in the environment variables"""
    value = os.getenv(key_name)
    if not value:
        raise exceptions.MissingAPIKey({"api_key": api_key})
    else:
        return value