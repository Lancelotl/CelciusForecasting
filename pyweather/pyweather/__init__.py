# Loading the .env file
import os
from pathlib import Path
from dotenv import load_dotenv
from . import exceptions

parent = Path(".")
env_path = parent / "variables.env"
load_dotenv(dotenv_path=env_path)

api_keys = [
    "ACCUWEATHER_API_KEY",
    "MET_CLIENT_SECRET",
    "MET_CLIENT_ID",
    "WEATHERCOM_API_KEY",
    "GWC_API_KEY",
]
for api_key in api_keys:
    if not os.getenv(api_key):
        raise exceptions.MissingAPIKey({"api_key": api_key})

# Importing the library's modules
from . import locations, forecast
