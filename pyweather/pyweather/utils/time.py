import pendulum
from ..exceptions import UnexpectedFormat


def utc_string_to_utc_datetime(time_utc):
    """Takes a conventionally formatted UTC string and returns a datetime object
    in utc

    Input:
        '2020-04-11T13:23:15Z'

    Output:
        Pendulum datetime object (UTC)
    """
    datetime_utc = pendulum.parse(time_utc).in_tz("UTC")
    return datetime_utc


def timestamp_to_utc_datetime(timestamp):
    """
    Input:
        1586743200

    Output:
        Pendulum datetime object (UTC)
    """
    datetime_utc = pendulum.from_timestamp(timestamp).in_tz("UTC")
    return datetime_utc


def hours_since_utc_datetime(then):
    """
    Input:
        Pendulum datetime object (UTC)

    Output:
        Number of hours elapsed (int)
    """
    now = pendulum.now().in_tz("UTC")
    return now.diff(then).in_hours()

def decaminutes_since_utc_datetime(then):
    """
    How many 10-minute away since the datetime?

    Input:
        Pendulum datetime object (UTC)

    Output:
        Number of decaminutes elapsed (int)
    """
    now = pendulum.now().in_tz("UTC")
    return now.diff(then).in_minutes() / 10

def parse_bomgovau_raw_footer_string_to_utc_datetime(raw_string):
    """Takes an unstructured date string of the type and returns a structured string instead.
    For bom.gov.au
    Input:
        '09:55 on Sunday 12 April 2020 (UTC)'
        
    Output:
        Pendulum datetime object (UTC)
    """
    tokens = raw_string.split(" ")
    hour_min, _, day_word, day_num, month_word, year_num, timezone = tokens
    structured_string = f"{day_num} {month_word} {year_num}, {hour_min}"
    datetime_utc = pendulum.from_format(
        structured_string, "DD MMMM YYYY, HH:mm", tz="UTC"
    )
    return datetime_utc


def parse_bomgovau_merge_date_as_dt_and_hour_as_string(
    date_dt, hour_string, target_timezone
):
    """
    For bom.gov.au

    Input:
        date_dt
            Pendulum datetime object (timezone is ignored)
        hour_string
            '1:00 AM' format "H:m A"
        target_timezone

    Output:
        Pendulum datetime object (UTC)
    """
    date_dt_string = date_dt.format("YYYY-DD-MM")
    merged = pendulum.from_format(
        date_dt_string + " " + hour_string, fmt="YYYY-DD-MM H:m A", tz=target_timezone
    )
    datetime_utc = merged.in_tz("UTC")
    return datetime_utc


def parse_bom_gov(date_attribute, timezone):
    """
    Input:
        'd2020-04-12'

    Output:
        Pendulum datetime object (local timezone)

    Context:
        <div class="forecast-day collapsible" id="d2020-04-12">
    """
    date = pendulum.from_format(date_attribute[1:], "YYYY-MM-DD", tz=timezone)
    return date


def format_accuweather(datetime_utc):
    """Formats a pendulum datetime object for Accuweather
    
    Input:
        Pendulum datetime object (UTC)
        
    Expected output:
        timestamp (int)

    Context:
        'EpochDateTime: 1586602800,
    """
    return datetime_utc.int_timestamp


def format_met(datetime_utc):
    """Formats a pendulum datetime object for MET

    Input:
        Pendulum datetime object (UTC)
        
    Expected output:
        '2020-04-11T09:00Z' (UTC)

    Context:
        'time': '2020-04-11T09:00Z',
    """
    return datetime_utc.format("YYYY-MM-DDTHH:mm") + "Z"


def format_yrno(datetime_utc):
    """
    Formats a pendulum datetime object for YRNO (MET.NO)

    Input:
        Pendulum datetime object (UTC)

    Expected output:
        (from_datetime, to_datetime)
        '2020-04-11T11:00:00Z', '2020-04-11T17:00:00Z'

    Context:
        <time datatype='forecast' from='2020-04-11T18:00:00Z' to='2020-04-11T18:00:00Z'>
    """
    format_yrno = "YYYY-MM-DDTHH:mm:ss"
    dt_form = datetime_utc.format(format_yrno) + "Z"
    dt_to = datetime_utc.add(hours=1).format(format_yrno) + "Z"
    return (dt_form, dt_to)


def format_standard(datetime_utc):
    """
    Expected output:
        '2020-04-11T11:00:00Z'
    """
    return datetime_utc.format("YYYY-MM-DDTHH:mm:ss") + "Z"


def format_bom(datetime_utc):
    """
    Simple pass-through to the format_standard
    """
    return format_standard(datetime_utc)


def local_string_to_utc_string(time_local, timezone, format_func):
    """Takes a local date as a string of the format:
        '2020-04-11T09:00'
    Returns the equivalent string in UTC
    """
    dt_local = pendulum.parse(time_local, tz=timezone)
    dt_utc = dt_local.in_tz("UTC")
    return format_func(dt_utc)
