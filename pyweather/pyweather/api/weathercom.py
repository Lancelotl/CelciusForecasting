import os
import random
import requests
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    local_string_to_weathercom_string,
    parse_weathercom,
)
from ..utils.conversions import farenheit_to_celcius, celcius_to_farenheit
from ..utils.api_keys import find_key
from ..utils.browser_profiles import Browser
from ..exceptions import HttpError, BadResponse, OutOfRange, UnexpectedFormat


ENDPOINT = "https://api.weather.com/v2/turbo/vt1hourlyForecast?apiKey={api_key}&format=json&geocode={latitude}%2C{longitude}&language=en-US&units={units}"

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))
SERVICE_NAME = "Weather.com"


def fetch(location_object, units="m"):
    """
    Input:
        units
            "m" (metric, celcius)
            "e" (imperial, farenheit)
    """
    if os.getenv("WEATHERCOM_API_KEY_ALT"):
        api_keys = ["WEATHERCOM_API_KEY", "WEATHERCOM_API_KEY_ALT"]
        api_key_name = random.choice(api_keys)
        api_key = find_key(api_key_name)
    else:
        api_key = find_key("WEATHERCOM_API_KEY")
    latitude, longitude = location_object["coordinates"]
    browser_profile = Browser()
    headers = browser_profile.headers
    r = requests.get(
        ENDPOINT.format(
            latitude=latitude, longitude=longitude, api_key=api_key, units=units
        ),
        headers=headers,
    )
    if r.ok:
        response = r.json()
        if not response:
            response_excerpt = r.text[:100]
            raise BadResponse(
                {
                    "service": SERVICE_NAME,
                    "message": "Empty page with code {r._status_code}. Full response: {response_excerpt}...",
                }
            )
        else:
            return response
    else:
        raise HttpError({"service": SERVICE_NAME, "response": r.status_code})


def retrieve_document(location_object):
    """Calls the API to fetch the document once only
    May perform additional transformation depending on the service

    For Weather.com, the retrieve document call with fetch twice
    for both celcius and farenheit

    It'll return temperatures that are an average of both:
    1) Fetch Celcius
        Convert to Farenheit
    2) Fetch Farenheit
    3) Average
    4) Convert to celcius
    """
    doc_farenheit = fetch(location_object, units="e")
    doc_celcius = fetch(location_object, units="m")

    temperatures = {}
    temperatures["farenheit"] = doc_farenheit.get("vt1hourlyForecast", {}).get(
        "temperature"
    )
    temperatures["celcius"] = doc_celcius.get("vt1hourlyForecast", {}).get(
        "temperature"
    )
    if not temperatures["farenheit"] or not temperatures["celcius"]:
        raise BadResponse(
            {"service": SERVICE_NAME, "message": "vt1hourlyForecast > temperature"}
        )

    # Converting all to decimals
    for u in ["farenheit", "celcius"]:
        temperatures[u] = [Decimal(str(elt)) for elt in temperatures[u]]
    # 1) Converting celcius to Farenheits
    temperatures["celcius"] = [
        celcius_to_farenheit(elt) for elt in temperatures["celcius"]
    ]

    # 3) Averaging
    farenheit_averaged = []
    for celcius_in_farenheit, farenheit in zip(
        temperatures["celcius"], temperatures["farenheit"]
    ):
        farenheit_averaged.append((celcius_in_farenheit + farenheit) / 2)

    # 4) Back to celcius
    celcius_average = [farenheit_to_celcius(elt) for elt in farenheit_averaged]

    doc_celcius["vt1hourlyForecast"]["temperature"] = celcius_average

    return doc_celcius


def find_in_document(location_object, target_local_time, document):
    """Finds the forecast for the desired time from the supplied API response

    Input:
        location_object
            {
                "coordinates": (-33.86, 151.21),
                "accuweather_key": 12481,
                "timezone": "Australia/Sydney",
                "bom.gov.au": "http://www.bom.gov.au/places/nsw/sydney/forecast/detailed/"
            }
        target_local_time
            '2020-04-11T09:00'

    Output:
        {
            "ok": True,
            "time_utc": "",
            "temperature_celcius": ""
        }
    """
    target_time_utc = local_string_to_utc_string(
        time_local=target_local_time,
        timezone=location_object["timezone"],
        format_func=format_standard,
    )
    target_time_formatted = local_string_to_weathercom_string(
        time_local=target_local_time, timezone=location_object["timezone"]
    )

    forecasts = document.get("vt1hourlyForecast", {})
    hours_local, temperatures = (
        forecasts.get("processTime"),
        forecasts.get("temperature"),
    )
    if not hours_local:
        raise BadResponse(
            {"service": SERVICE_NAME, "message": "vt1hourlyForecast > processTime"}
        )
    if not temperatures:
        raise BadResponse(
            {"service": SERVICE_NAME, "message": "vt1hourlyForecast > temperatures"}
        )
    if len(hours_local) != len(temperatures):
        raise UnexpectedFormat(
            {
                "service": SERVICE_NAME,
                "message": "Different number of hours and temperatures",
            }
        )

    for hour, temperature in zip(hours_local, temperatures):
        if hour == target_time_formatted:
            temperature = round(Decimal(temperature), DECIMAL_PLACES)
            return {
                "ok": True,
                "time_utc": target_time_utc,
                "temperature_celcius": temperature,
                "forecast_age_hours": None,
                "forecast_issue_time": None,
            }
    else:
        # Exhausted list of forecasts
        latest_time = format_standard(parse_weathercom(hour))
        raise OutOfRange(
            {
                "service": SERVICE_NAME,
                "message": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )
