import os
import random
from ..exceptions import MissingAPIKey


def find_key(key_name):
    """Attempts to find the following API key in the environment variables"""
    value = os.getenv(key_name)
    if not value:
        raise MissingAPIKey({"api_key": key_name})
    else:
        return value