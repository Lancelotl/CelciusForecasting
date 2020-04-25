"""
Coordinates from
https://docs.google.com/spreadsheets/d/1q45g7Su1dc6tUyMNBNJ1hmr5A_Ddavklg2vbTgG2K90/edit#gid=0
"""

LOCATIONS = {
    "SYDNEY": {
        "coordinates": (-33.86, 151.21),
        "accuweather_location_key": 12481,
        "timezone": "Australia/Sydney",
        "bom.gov.au": "http://www.bom.gov.au/places/nsw/sydney/forecast/detailed/",
    },
    "MELBOURNE": {
        "coordinates": (-37.83, 144.98),
        "accuweather_location_key": 3497808,
        "timezone": "Australia/Melbourne",
        "bom.gov.au": "http://www.bom.gov.au/places/vic/melbourne/forecast/detailed/",
    },
    "BRISBANE": {
        "coordinates": (-27.48, 153.04),
        "accuweather_location_key": 1404,
        "timezone": "Australia/Brisbane",
        "bom.gov.au": "http://www.bom.gov.au/places/qld/brisbane/forecast/detailed/",
    },
}
