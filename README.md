# CelciusForecasting (pyweather)
 Retrieving multi-source temperature forecasts by coordinates.


## Example
```python
from pyweather.forecast import Forecast
from pyweather.locations import LOCATIONS
from pyweather.services import BOM, MET, YRNO, ACCUWEATHER, WEATHERCOM, GWC, AERIS

from pprint import pprint

CITIES = ["SYDNEY", "MELBOURNE", "BRISBANE"]
TOMORROW_1_PM = "2020-04-14T13:00"
SERVICES = [BOM, MET, YRNO, ACCUWEATHER, WEATHERCOM, GWC, AERIS]

for city in CITIES:
    forecast = Forecast(LOCATIONS[city], TOMORROW_1_PM, services=SERVICES)
    f_avg, f_max, f_min = forecast.aggregated["average"], forecast.aggregated["max"], forecast.aggregated["min"]
    print(f"{city}")
    print(f"""    Average: {f_avg}°,    Max: {f_max}°,    Min: {f_min}°""")
    print("\n")
```

## Weather forecasting services
Currently supports 7 weather forecasting services!
- Australian Bureau of Meteorology (BOM)
- The MET Office (MET)
- Norwegian Meteorological Institute (YRNO)
- Accuweather (ACCUWEATHER)
- Weather.com or "The Weather Channel" (WEATHERCOM)
- Global Weather Corporation (GWC)
- Aeris Weather (AERIS)


## API Keys
 To use the Accuweather and MET APIs, please create a variables.env file in your current directory with your own API keys for the following services:

```
ACCUWEATHER_API_KEY = ""

MET_CLIENT_ID = ""
MET_CLIENT_SECRET = ""

WEATHERCOM_API_KEY = ""

GWC_API_KEY = ""

AERIS_CLIENT_ID = ""
AERIS_CLIENT_SECRET = ""
```

 You can also optionally pass the following options in this variables.env file:
```
DECIMAL_PLACES = 2
```