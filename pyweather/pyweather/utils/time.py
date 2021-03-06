import pendulum


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
        '12:01 on Friday  1 May 2020 (UTC)'
        
    Output:
        Pendulum datetime object (UTC)
    """
    # Remove any duplicate spaces first
    raw_string = raw_string.replace("  ", " ")

    tokens = raw_string.split(" ")
    hour_min, _, day_word, day_num, month_word, year_num, timezone = tokens
    structured_string = f"{day_num} {month_word} {year_num}, {hour_min}"
    datetime_utc = pendulum.from_format(
        structured_string, "D MMMM YYYY, HH:mm", tz="UTC"
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
        date_dt_string + " " + hour_string, fmt="YYYY-DD-MM h:m A", tz=target_timezone
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


def parse_weathercom(raw_string):
    """For Weather.com

    Input:
        raw_string
            '2020-05-07T03:00:00+1000'

    Output:
        Pendulum datetime object (UTC)
    """
    return pendulum.parse(raw_string).in_tz("UTC")


def parse_aeris(raw_string):
    """For the Aeris API

    Input:
        raw_string
            2020-05-26T03:00:00+10:00

    Output:
        Pendulum datetime object (UTC)
    """
    return pendulum.parse(raw_string).in_tz("UTC")


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


def local_string_to_weathercom_string(time_local, timezone):
    """Takes a local date as a string of the format:
        '2020-04-11T09:00'
    Returns the equivalent string in UTC
        '2020-05-09T00:00:00+1000'
    """
    dt_local = pendulum.parse(time_local, tz=timezone)
    return dt_local.format("YYYY-MM-DDTHH:mm:ssZZ")


def local_string_to_aeris_string(time_local, timezone):
    """Takes a local date as a string of the format:
        '2020-04-11T09:00'
    Returns the equivalent string in UTC
        '2020-05-26T03:00:00+10:00'
    """
    dt_local = pendulum.parse(time_local, tz=timezone)
    return dt_local.format("YYYY-MM-DDTHH:mm:ssZ")


def datetime_to_simple_string(date_dt):
    """Datetime -> simple string

    Input:
        Pendulum datetime object (UTC)

    Expected output:
        '2020-04-11T09:00'
    """
    return date_dt.format("YYYY-MM-DDTHH:mm")


def hours_between_datetimes(start, end):
    """Computes the number of hours between two dates as strings:
    Input:
        '2020-04-26T13:00',
        '2020-04-26T16:00'

    Expected output:
        3 hours
    """
    return end.diff(start).in_hours()


def count_to(n):
    return range(1, n + 1)


def local_string_to_range_of_local_strings(
    time_local_start, time_local_end=None, next_n_hours=None
):
    """Returns a range of dates as strings:
    Input:
        time_local_start = '2020-04-26T13:00'

        End (optional):
            time_local_end = '2020-04-26T16:00'

        N-hours (optional):
            next_n_hours = 6


    Expected output:
        [
            '2020-04-26T13:00',
            '2020-04-26T14:00',
            '2020-04-26T15:00',
            '2020-04-26T16:00',
            '2020-04-26T17:00'
        ]
    """
    if not time_local_end and not next_n_hours:
        return []

    start = pendulum.parse(time_local_start)
    if time_local_end:
        end = pendulum.parse(time_local_end)
        next_n_hours = hours_between_datetimes(start=start, end=end)

    datetimes = [time_local_start]
    for i in count_to(
        next_n_hours - 1
    ):  # Otherwise captures (next hour + n) instead of just (n next hours)
        datetimes.append(start.add(hours=i))

    datetime_strings = [datetime_to_simple_string(elt) for elt in datetimes]

    return datetime_strings


def next_hour_in_tz():
    """Returns a local datetime for the next round hour in the target timezone
    Input:
        Timezone
            "Australia/Sydney"

    Expected output:
        Pendulum datetime object (local)
    """
    now = pendulum.now().in_tz("UTC")
    next_hour = now.start_of("hour").add(hours=1)

    return next_hour


def gwc_next_24h_start_end():
    """Returns a start and end datetimes (local) used to query the GWC API
    Input:
        Timezone
            "Australia/Sydney"

    Expected output:
        Tuple (start, end)
        (
            Pendulum datetime object (local),
            Pendulum datetime object (local)
        )
    """
    start = next_hour_in_tz()
    end = start.add(hours=24)

    return start, end


def format_gwc_url_dates(datetime_local):
    """Formats a pendulum datetime object for GWC
    This is the date that is used in the URL

    Input:
        Pendulum datetime object (local)

    Expected output:
        '20200511T14'

    Context:
        https://.../20200511T14-20200512T13timeinterval...
    """

    return datetime_local.format("YYYYMMDDTHH")


def local_string_to_gwc_string_search(time_local, timezone):
    """Takes a local date as a string of the format:
        '2020-05-12T09:00'

    Returns the equivalent string in UTC
        'Tue May 12 09:00:00 2020'
    """
    dt_local = pendulum.parse(time_local, tz=timezone)

    return dt_local.format("ddd MMM DD HH:mm:ss YYYY")


def normalize_gwc(raw_string):
    """Normalizes the GWC dates as strings.

    Helps removes timezone names (EST) that are inconsistent
    with pendulum (AEST)

    Input:
        'Tue May 12 23:00:00 EST 2020'

    Output:
        'Tue May 12 23:00:00 2020'
    """
    stripped = raw_string.split(" ")
    stripped = " ".join(stripped[:-2] + stripped[-1:])
    return stripped


def parse_gwc(raw_string, timezone):
    """Parses the GWC

    Input:
        raw_string
            'Tue May 12 23:00:00 EST 2020'

        target_timezone
            'Australia/Sydney'

    Output:
        Pendulum datetime object (UTC)
    """
    stripped = normalize_gwc(raw_string)
    parsed = pendulum.from_format(stripped, "ddd MMM DD HH:mm:ss YYYY").in_tz(timezone)

    return parsed
