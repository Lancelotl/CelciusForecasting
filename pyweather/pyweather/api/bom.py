import os
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from decimal import InvalidOperation
from ..utils.time import (
    local_string_to_utc_string,
    format_standard,
    parse_bomgovau_raw_footer_string_to_utc_datetime,
    parse_bomgovau_merge_date_as_dt_and_hour_as_string,
    parse_bom_gov,
    hours_since_utc_datetime,
    decaminutes_since_utc_datetime,
    utc_string_to_utc_datetime,
)
from ..exceptions import HttpError, BadResponse, UnexpectedFormat, OutOfRange

DECIMAL_PLACES = int(os.getenv("DECIMAL_PLACES", 2))


def fetch(location_object):
    url = location_object["bom.gov.au"]
    r = requests.get(url)
    if r.ok:
        return r.text
    else:
        raise HttpError({"service": "Bom.gov.au", "response": r.status_code})


def parse_string_temperature(raw_string):
    """Util function to parse the temperature strings found on the BOM website

    Input:
        "–"
        "16"

    Ouput:
        Decimal(0)
        Decimal(16)
    """
    if raw_string == "–":
        return None
    try:
        return Decimal(raw_string)
    except InvalidOperation:
        raise UnexpectedFormat(
            {
                "service": "Bom.gov.au",
                "key": f"Could not parse as decimal the temperature {raw_string}",
            }
        )


def soup_to_forecast_object(soup, timezone):
    """Takes a soup object and returns an object listing all forecasts
    found in the page

    Output:
        {
            "issue_time": "2020-04-11T11:00:00Z",
            "forecasts": 
                [
                    {
                        "time_utc": "2020-04-11T11:00:00Z",
                        "temperature_celcius": 12
                    },
                    {
                        "time_utc": "2020-04-11T12:00:00Z",
                        "temperature_celcius": 13
                    }
                ]
        }
    """
    forecast = {}

    # Retrieving the forecast issue time
    footer = soup.find("div", attrs={"id": "footer"})
    if not footer:
        raise BadResponse({"service": "Bom.gov.au", "key": "div id=footer"})
    timestamp_text = footer.find("p", attrs={"id": "timestamp"}).text.strip()
    if not timestamp_text:
        raise BadResponse({"service": "Bom.gov.au", "key": "p id=timestamp"})
    str_padding = "This page was created at "  # String to be removed
    if not str_padding in timestamp_text:
        raise UnexpectedFormat(
            {"service": "Bom.gov.au", "key": "Did not find 'This page was created at'"}
        )
    timestamp_text = timestamp_text.replace(str_padding, "")
    issue_time = format_standard(
        parse_bomgovau_raw_footer_string_to_utc_datetime(timestamp_text)
    )
    forecast["issue_time"] = issue_time

    # Retrieving the individual forecasts
    forecast["forecasts"] = []
    days = soup.find_all("div", attrs={"class": "forecast-day collapsible"})
    if not days:
        BadResponse(
            {"service": "Bom.gov.au", "key": "div class='forecast-day collapsible'"}
        )
    for day in days:
        try:
            date_string = day["id"]
        except KeyError:
            raise BadResponse({"service": "Bom.gov.au", "key": "day id=''"})
        date = parse_bom_gov(date_string, timezone)
        search_string = "temperature"
        tables = day.find_all("table")
        if not tables:
            raise BadResponse({"service": "Bom.gov.au", "key": "table"})
        for table in tables:
            if search_string in table["summary"].lower():
                temperatures_table = table
                break
        else:
            # Exhausted list without finding search string
            raise BadReponse(
                {
                    "service": "Bom.gov.au",
                    "key": f"Did not find a table with '{search_string}' in",
                }
            )

        # Listing the local times
        #
        #

        ### Skipping the first one:
        ###   <th class="first">At</th>
        times_raw = table.find("thead").find_all("th")[1:]
        if not times_raw:
            raise BadResponse({"service": "Bom.gov.au", "key": "thead > th"})
        times_raw = [elt.text.strip() for elt in times_raw]

        ### Composing a full date string
        ### Prepend with the date
        time_utc_strings = []
        for t in times_raw:
            time = format_standard(
                parse_bomgovau_merge_date_as_dt_and_hour_as_string(
                    date_dt=date, hour_string=t, target_timezone=timezone
                )
            )
            time_utc_strings.append(time)

        # Listing the temperatures
        #
        #
        temperatures_raw = temperatures_table.find("tbody")
        if not temperatures_raw:
            raise BadResponse({"service": "Bom.gov.au", "key": "tbody"})
        search_string = "Air temperature (°C)"
        tr_list = temperatures_raw.find_all("tr")
        if not tr_list:
            raise BadResponse({"service": "Bom.gov.au", "key": "tbody > tr"})
        for tmp_block in tr_list:
            if search_string in tmp_block.text:
                temperature_values = tmp_block.find_all("td")
                if not temperature_values:
                    raise BadResponse(
                        {"service": "Bom.gov.au", "key": "tbody > tr > td"}
                    )
                temperature_values = [
                    parse_string_temperature(elt.text.strip())
                    for elt in temperature_values
                ]
                break
        else:
            # Exhausted list without finding search string
            raise UnexpectedFormat(
                {
                    "service": "Bom.gov.au",
                    "key": f"Did not find a table with '{search_string}' in",
                }
            )

        # Ensuring as many hours as temperatures
        if len(time_utc_strings) != len(temperature_values):
            raise BadReponse(
                {
                    "service": "Bom.gov.au",
                    "key": f"Date: {date}. Found {len(time_utc_strings)} hours, but {len(temperature_values)} hours",
                }
            )

        # Saving the temperature forecasts
        for time, temperature in zip(time_utc_strings, temperature_values):
            if temperature:
                # Otherwise, the cell is empty because this time has passed
                forecast["forecasts"].append(
                    {"time_utc": time, "temperature_celcius": temperature}
                )
    return forecast


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

    html = fetch(location_object)
    soup = BeautifulSoup(html, "lxml")

    # Composing a forecast object
    forecast_object = soup_to_forecast_object(soup, location_object["timezone"])

    # Retrieving the issue time, forecast age
    # Debug
    issue_time = forecast_object["issue_time"]
    forecast_age_hours = hours_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )
    forecast_age_decaminutes = decaminutes_since_utc_datetime(
        utc_string_to_utc_datetime(issue_time)
    )

    # Retrieving the forecasted temperature
    forecasts = forecast_object["forecasts"]
    for forecast in forecasts:
        if forecast["time_utc"] == target_time_utc:
            temperature = round(
                Decimal(forecast["temperature_celcius"]), DECIMAL_PLACES
            )

            return {
                "ok": True,
                "time_utc": target_time_utc,
                "temperature_celcius": temperature,
                "forecast_age_hours": None,  # The issue time appears incorrect
                "forecast_age_decaminutes": None,
                "forecast_issue_time": None,  # The issue time appears incorrect
            }
    else:
        # Exhausted list of forecasts
        raise OutOfRange(
            {
                "service": "Bom.gov.au",
                "key": f"Could not find a forecast for {target_time_utc}. Latest is {forecast['time_utc']}.",
            }
        )
