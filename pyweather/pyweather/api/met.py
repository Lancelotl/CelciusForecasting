import os
import requests
from decimal import Decimal
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    format_met,
    hours_since_utc_datetime,
    decaminutes_since_utc_datetime,
    utc_string_to_utc_datetime,
)
from ..utils.api_keys import find_key
from ..exceptions import HttpError, BadResponse, OutOfRange

ENDPOINT = "https://api-metoffice.apiconnect.ibmcloud.com/metoffice/production/v0/forecasts/point/hourly?excludeParameterMetadata=123&includeLocationName=true&latitude={latitude}&longitude={longitude}"

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))
SERVICE_NAME = "Met"


def fetch(location_object):
    # Checking API
    api_client_secret, api_client_id = (
        find_key("MET_CLIENT_SECRET"),
        find_key("MET_CLIENT_ID"),
    )
    latitude, longitude = location_object["coordinates"]
    r = requests.get(
        ENDPOINT.format(latitude=latitude, longitude=longitude),
        headers={
            "X-IBM-Client-Secret": api_client_secret,
            "X-IBM-Client-Id": api_client_id,
        },
    )
    if r.ok:
        return r.json()
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
        format_func=format_met,
    )

    response = fetch(location_object)

    # Retrieving the issue time, forecast age
    try:
        issue_time = response["features"][0]["properties"]["modelRunDate"]
    except KeyError:
        raise BadResponse({"service": SERVICE_NAME, "key": "features/properties/modelRunDate"})
    forecast_age_hours = hours_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )
    forecast_age_decaminutes = decaminutes_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )

    # Retrieving the forecasted temperature
    try:
        forecasts = response["features"][0]["properties"]["timeSeries"]
    except KeyError:
        raise BadResponse({"service": SERVICE_NAME, "key": "features/properties/timeSeries"})

    for forecast in forecasts:
        try:
            time = forecast["time"]
        except KeyError:
            raise BadResponse({"service": SERVICE_NAME, "key": "time"})
        if time == target_time_formatted:
            try:
                temperature = forecast["screenTemperature"]
            except KeyError:
                raise BadResponse({"service": SERVICE_NAME, "key": "screenTemperature"})
            temperature = round(Decimal(str(temperature)), DECIMAL_PLACES)

            issue_time_formatted = format_standard(
                utc_string_to_utc_datetime(issue_time)
            )
            return {
                "ok": True,
                "time_utc": target_time_utc,
                "temperature_celcius": temperature,
                "forecast_age_hours": forecast_age_hours,
                "forecast_age_decaminutes": forecast_age_decaminutes,
                "forecast_issue_time": issue_time_formatted,
            }
    else:
        # Exhausted list of forecasts
        latest_time = time
        raise OutOfRange(
            {
                "service": "Accuweather",
                "key": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )


def retrieve_document(location_object):
    """Calls the API to fetch the document once only
    May perform additional transformation depending on the service
    """
    return fetch(location_object)


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
        format_func=format_met,
    )

    response = document

    # Retrieving the issue time, forecast age
    try:
        issue_time = response["features"][0]["properties"]["modelRunDate"]
    except KeyError:
        raise BadResponse({"service": SERVICE_NAME, "key": "features/properties/modelRunDate"})
    forecast_age_hours = hours_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )
    forecast_age_decaminutes = decaminutes_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )

    # Retrieving the forecasted temperature
    try:
        forecasts = response["features"][0]["properties"]["timeSeries"]
    except KeyError:
        raise BadResponse({"service": SERVICE_NAME, "key": "features/properties/timeSeries"})

    for forecast in forecasts:
        try:
            time = forecast["time"]
        except KeyError:
            raise BadResponse({"service": SERVICE_NAME, "key": "time"})
        if time == target_time_formatted:
            try:
                temperature = forecast["screenTemperature"]
            except KeyError:
                raise BadResponse({"service": SERVICE_NAME, "key": "screenTemperature"})
            temperature = round(Decimal(str(temperature)), DECIMAL_PLACES)

            issue_time_formatted = format_standard(
                utc_string_to_utc_datetime(issue_time)
            )
            return {
                "ok": True,
                "time_utc": target_time_utc,
                "temperature_celcius": temperature,
                "forecast_age_hours": forecast_age_hours,
                "forecast_age_decaminutes": forecast_age_decaminutes,
                "forecast_issue_time": issue_time_formatted,
            }
    else:
        # Exhausted list of forecasts
        latest_time = time
        raise OutOfRange(
            {
                "service": "Accuweather",
                "key": f"Could not find a forecast for {target_time_utc}. Latest is {latest_time}.",
            }
        )
