import os
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    format_yrno,
    utc_string_to_utc_datetime,
    hours_since_utc_datetime,
    decaminutes_since_utc_datetime,
)
from ..exceptions import HttpError, BadResponse

ENDPOINT = (
    "https://api.met.no/weatherapi/locationforecast/1.9/?lat={latitude}&lon={longitude}"
)

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))
SERVICE_NAME = "Yr.no"


def fetch(location_object):
    latitude, longitude = location_object["coordinates"]
    r = requests.get(ENDPOINT.format(latitude=latitude, longitude=longitude))
    if r.ok:
        return r.text
    else:
        raise HttpError({"service": SERVICE_NAME, "response": r.status_code})


def retrieve(location_object, target_local_time):
    """Retrieves the forecast for the desired time from the API
    
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
    target_time_formatted = local_string_to_utc_string(
        time_local=target_local_time,
        timezone=location_object["timezone"],
        format_func=format_yrno,
    )

    xml = fetch(location_object)
    soup = BeautifulSoup(xml, "lxml")

    # Retrieving the issue time, forecast age
    metadata = soup.find("model", attrs={"name": "met_public_forecast"})
    if not metadata:
        raise BadResponse({"service": SERVICE_NAME, "key": "model name=met_public_forecast"})
    try:
        issue_time = metadata["runended"]
    except KeyError:
        BadResponse({"service": SERVICE_NAME, "key": "model/runended"})
    forecast_age_hours = hours_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )
    forecast_age_decaminutes = decaminutes_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )

    # Retrieving the forecasted temperature
    pointdata = soup.find("product", attrs={"class": "pointData"})
    if not pointdata:
        raise BadResponse({"service": SERVICE_NAME, "key": "product class=pointData"})
    forecast = pointdata.find(
        name="time",
        attrs={
            "datatype": "forecast",
            "from": target_time_formatted,
            "to": target_time_formatted,
        },
    )
    if not forecast:
        raise BadResponse({"service": SERVICE_NAME, "key": "time datatype=forecast"})
    try:
        temperature = forecast.find("location").find(
            name="temperature", attrs={"id": "TTT", "unit": "celsius"}
        )["value"]
    except KeyError:
        BadResponse({"service": SERVICE_NAME, "key": "temperature/value"})
    if not temperature:
        BadResponse({"service": SERVICE_NAME, "key": "temperature id=TTT"})
    temperature = round(Decimal(temperature), DECIMAL_PLACES)

    if temperature:
        return {
            "ok": True,
            "time_utc": target_time_utc,
            "temperature_celcius": temperature,
            "forecast_age_hours": forecast_age_hours,
            "forecast_age_decaminutes": forecast_age_decaminutes,
            "forecast_issue_time": issue_time,
        }
    else:
        return {"ok": False}


def retrieve_document(location_object):
    """Calls the API to fetch the document once only
    May perform additional transformation depending on the service
    """
    xml = fetch(location_object)
    soup = BeautifulSoup(xml, "lxml")
    return soup


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
    target_time_formatted = local_string_to_utc_string(
        time_local=target_local_time,
        timezone=location_object["timezone"],
        format_func=format_yrno,
    )

    xml = document

    # Retrieving the issue time, forecast age
    metadata = xml.find("model", attrs={"name": "met_public_forecast"})
    if not metadata:
        raise BadResponse({"service": SERVICE_NAME, "key": "model name=met_public_forecast"})
    try:
        issue_time = metadata["runended"]
    except KeyError:
        BadResponse({"service": SERVICE_NAME, "key": "model/runended"})
    forecast_age_hours = hours_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )
    forecast_age_decaminutes = decaminutes_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )

    # Retrieving the forecasted temperature
    pointdata = xml.find("product", attrs={"class": "pointData"})
    if not pointdata:
        raise BadResponse({"service": SERVICE_NAME, "key": "product class=pointData"})
    forecast = pointdata.find(
        name="time",
        attrs={
            "datatype": "forecast",
            "from": target_time_formatted,
            "to": target_time_formatted,
        },
    )
    if not forecast:
        raise BadResponse({"service": SERVICE_NAME, "key": "time datatype=forecast"})
    try:
        temperature = forecast.find("location").find(
            name="temperature", attrs={"id": "TTT", "unit": "celsius"}
        )["value"]
    except KeyError:
        BadResponse({"service": SERVICE_NAME, "key": "temperature/value"})
    if not temperature:
        BadResponse({"service": SERVICE_NAME, "key": "temperature id=TTT"})
    temperature = round(Decimal(temperature), DECIMAL_PLACES)

    if temperature:
        return {
            "ok": True,
            "time_utc": target_time_utc,
            "temperature_celcius": temperature,
            "forecast_age_hours": forecast_age_hours,
            "forecast_age_decaminutes": forecast_age_decaminutes,
            "forecast_issue_time": issue_time,
        }
    else:
        return {"ok": False}
