# CelciusForecasting
 Retrieving multi-source temperature forecasts by coordinates.


## Example
```python
from pyweather.forecast import Forecast
from pyweather.locations import LOCATIONS
from pyweather.services import BOM, MET, YRNO, ACCUWEATHER

from pprint import pprint

CITIES = ["SYDNEY", "MELBOURNE", "BRISBANE"]
TOMORROW_1_PM = "2020-04-14T13:00"
SERVICES = [BOM, MET, YRNO, ACCUWEATHER]

for city in CITIES:
    forecast = Forecast(LOCATIONS[city], TOMORROW_1_PM, services=SERVICES)
    f_avg, f_max, f_min = forecast.aggregated["average"], forecast.aggregated["max"], forecast.aggregated["min"]
    print(f"{city}")
    print(f"""    Average: {f_avg}°,    Max: {f_max}°,    Min: {f_min}°""")
    print("\n")
```

## API Keys
 To use Accuweather and the MET, please create a variables.env file in your current directory with your own API keys for the following services:

```
ACCUWEATHER_API_KEY = ""

MET_CLIENT_SECRET = ""
MET_CLIENT_ID = ""
```

 You can also optionally pass the following options in this variables.env file:
```
DECIMAL_PLACES = 2
```