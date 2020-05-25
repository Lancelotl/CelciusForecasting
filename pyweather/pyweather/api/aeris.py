import os
import random
import requests
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    local_string_to_aeris_string,
    parse_aeris,
)
from ..utils.browser_profiles import AerisMobileApp
from ..utils.api_keys import find_key
from ..exceptions import HttpError, BadResponse, OutOfRange, UnexpectedFormat


ENDPOINT = "https://api.aerisapi.com/forecasts/{latitude},{longitude}?client_id={client_id}&client_secret={client_secret}&filter=1hr,precise&plimit=24"

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))
SERVICE_NAME = "Aeris"


def fetch(location_object):
    """
    """
    api_id = find_key("AERIS_CLIENT_ID")
    api_secret = find_key("AERIS_CLIENT_SECRET")
    latitude, longitude = location_object["coordinates"]
    browser_profile = AerisMobileApp()
    headers = browser_profile.headers
    r = requests.get(
        ENDPOINT.format(
            latitude=latitude,
            longitude=longitude,
            client_id=api_id,
            client_secret=api_secret,
            headers=headers,
        )
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

    For Aeris, simplifies the response and returns only the periods (forecasts)
    """
    document = fetch(location_object)
    return document


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
    target_time_formatted = local_string_to_aeris_string(
        time_local=target_local_time, timezone=location_object["timezone"]
    )

    if not document.get("success"):
        # The response suggested an error
        raise BadResponse(
            {
                "service": SERVICE_NAME,
                "message": f"Response suggested the following error: {document.get('error')}",
            }
        )

    response = document.get("response", [])
    if not response:
        raise BadResponse({"service": SERVICE_NAME, "message": "response[0] empty"})
    forecasts = response[0].get("periods")
    if not forecasts:
        raise BadResponse({"service": SERVICE_NAME, "message": "response[0] > periods"})
    for forecast in forecasts:
        hour = forecast.get("validTime")
        if not hour:
            raise BadResponse(
                {
                    "service": SERVICE_NAME,
                    "message": "response[0] > periods > validTime",
                }
            )
        hour_iso = forecast.get("dateTimeISO")
        if not hour_iso:
            raise BadResponse(
                {
                    "service": SERVICE_NAME,
                    "message": "response[0] > periods > dateTimeISO",
                }
            )
        if hour == hour_iso:
            # Confirms this is a forecast for an individual hour
            if hour == target_time_formatted:
                temperature = forecast.get(
                    "maxTempC"
                )  # "maxTempC" and "minTempC" are the same in that context
                if not temperature:
                    raise BadResponse(
                        {
                            "service": SERVICE_NAME,
                            "message": "response[0] > periods > maxTempC",
                        }
                    )
                # Transforming to str then Decimal then rounding
                temperature = round(Decimal(str(temperature)), DECIMAL_PLACES)
                return {
                    "ok": True,
                    "time_utc": target_time_utc,
                    "temperature_celcius": temperature,
                    "forecast_age_hours": None,
                    "forecast_issue_time": None,
                }
    else:
        # Exhausted list of forecasts
        latest_time = format_standard(parse_aeris(hour))
        raise OutOfRange(
            {
                "service": SERVICE_NAME,
                "message": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )
