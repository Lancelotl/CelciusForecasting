import os
import requests
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    format_accuweather,
    timestamp_to_utc_datetime,
)
from ..utils.api_keys import find_key
from ..exceptions import HttpError, BadResponse, UnexpectedFormat, OutOfRange


ENDPOINT = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}?apikey={api_key}&language=en-gb&details=true&metric=true"

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))


def fetch(location_object):
    api_key = find_key("ACCUWEATHER_API_KEY")
    r = requests.get(
        ENDPOINT.format(
            location_key=location_object["accuweather_location_key"], api_key=api_key,
        )
    )
    if r.ok:
        return r.json()
    else:
        raise HttpError({"service": "Accuweather", "response": r.status_code})


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
        format_func=format_accuweather,
    )

    forecasts = fetch(location_object)

    for forecast in forecasts:
        try:
            time = forecast["EpochDateTime"]
        except KeyError:
            raise BadResponse({"service": "Accuweather", "key": "EpochDateTime"})
        if time == target_time_formatted:
            try:
                temperature = forecast["Temperature"]["Value"]
            except KeyError:
                raise BadResponse(
                    {"service": "Accuweather", "key": "Temperature/Value"}
                )
            temperature = round(Decimal(temperature), DECIMAL_PLACES)
            try:
                unit = forecast["Temperature"]["Unit"]
            except KeyError:
                raise BadResponse({"service": "Accuweather", "key": "Temparature/Unit"})
            if unit != "C":
                raise UnexpectedFormat({"service": "Accuweather", "key": "unit == C"})

            return {
                "ok": True,
                "time_utc": target_time_utc,
                "temperature_celcius": temperature,
                "forecast_age_hours": None,
                "forecast_issue_time": None,
            }
    else:
        # Exhausted list of forecasts
        latest_time = format_standard(timestamp_to_utc_datetime(time))
        raise OutOfRange(
            {
                "service": "Accuweather",
                "key": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )
