# Loading the .env file
import os
from pathlib import Path
from dotenv import load_dotenv
from . import exceptions

PROJECT_PATH = os.getenv("PROJECT_PATH")
if PROJECT_PATH:
    env_variables_filepath = Path(PROJECT_PATH) / "variables.env"
else:
    parent = Path(".")
    env_variables_filepath = parent / "variables.env"

load_dotenv(dotenv_path=env_variables_filepath)

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
