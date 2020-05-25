import os
import requests
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    gwc_next_24h_start_end,
    format_gwc_url_dates,
    local_string_to_gwc_string_search,
    parse_gwc,
    normalize_gwc,
)
from ..utils.conversions import farenheit_to_celcius
from ..utils.api_keys import find_key
from ..utils.browser_profiles import Browser
from ..exceptions import HttpError, BadResponse, UnexpectedFormat, OutOfRange


ENDPOINT = "https://service.globalweathercorp.com/webservices/resources/v2/weatherdata/{latitude}/{longitude}/{start_date}-{end_date}timeinterval=%7B1%7D?gwctoken={api_key}"

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))
SERVICE_NAME = "GWC"


def fetch(location_object, start_date, end_date):
    """
    """
    api_key = find_key("GWC_API_KEY")
    latitude, longitude = location_object["coordinates"]
    browser_profile = Browser()
    headers = browser_profile.headers
    r = requests.get(
        ENDPOINT.format(
            latitude=latitude,
            longitude=longitude,
            api_key=api_key,
            start_date=start_date,
            end_date=end_date,
        ),
        headers=headers,
    )
    if r.ok:
        return r.json()
    else:
        raise HttpError({"service": SERVICE_NAME, "response": r.status_code})


def retrieve_document(location_object):
    """Calls the API to fetch the document once only
    May perform additional transformation depending on the service

    For GWC, the retrieve document call will need to supply both a start_date and end_date
    down to the fetch() function

    Returns a document that contains Farenheit temperatures
    """
    start_date, end_date = gwc_next_24h_start_end()
    start_date, end_date = (
        format_gwc_url_dates(start_date),
        format_gwc_url_dates(end_date),
    )

    doc_farenheit = fetch(
        location_object=location_object, start_date=start_date, end_date=end_date
    )

    return doc_farenheit


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
    target_time_formatted = local_string_to_gwc_string_search(
        time_local=target_local_time, timezone=location_object["timezone"]
    )

    forecasts = document.get("times", [])
    for forecast in forecasts:
        hour = forecast.get("validDate")
        if not hour:
            raise BadResponse({"service": SERVICE_NAME, "message": "times > validDate"})
        normalized_hour = normalize_gwc(hour)
        if normalized_hour == target_time_formatted:
            points = forecast.get("points")
            if not points:
                raise BadResponse(
                    {"service": SERVICE_NAME, "message": "times > points"}
                )
            for measurement in points:
                data_type = measurement.get("dataType")
                if not data_type:
                    raise BadResponse(
                        {
                            "service": SERVICE_NAME,
                            "message": "times > points > dataType",
                        }
                    )
                if data_type == "temp":
                    temperature = measurement.get("value")
                    if not temperature:
                        raise BadResponse(
                            {
                                "service": SERVICE_NAME,
                                "message": "times > points > value",
                            }
                        )
                    temperature = farenheit_to_celcius(temperature)
                    temperature = round(Decimal(temperature), DECIMAL_PLACES)
                    return {
                        "ok": True,
                        "time_utc": target_time_utc,
                        "temperature_celcius": temperature,
                        "forecast_age_hours": None,
                        "forecast_issue_time": None,
                    }
            else:
                # Found no point with a 'dataType' == 'temp'
                raise UnexpectedFormat(
                    {
                        "service": SERVICE_NAME,
                        "message": "Found no dataType in points with the name 'temp'",
                    }
                )
    else:
        # Exhausted list of forecasts
        latest_time = format_standard(
            parse_gwc(hour, timezone=location_object["timezone"])
        )
        raise OutOfRange(
            {
                "service": SERVICE_NAME,
                "message": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )
