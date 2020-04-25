from .services import BOM, MET, ACCUWEATHER, YRNO
from .exceptions import OutOfRange
from decimal import Decimal


def soothing(hours):
    """A soothing factors to compute exponentially decaying data
    i.e. older forecasts shouldn't count as much as more recent forecasts
    """
    return 2 / (Decimal(hours) + 1)


def sumproduct(*lists):
    """Excel-style sumproduct function"""
    return sum([x * y for x, y in zip(*lists)])


class Forecast:
    def __init__(self, location_object, local_date, services=[BOM, MET, ACCUWEATHER, YRNO]):
        self.location_object = location_object
        self.local_date = local_date
        self.services = services
        self.detailed = self._fetch_forecast()
        self.aggregated = self._compute_aggregates()

    def _fetch_forecast(self):
        """Forecasts the weather by calling all services

        Output:
            {
                "aggregated": {
                    "average": 14.6,
                    "min": 14.3,
                    "max": 14.8
                },
                "forecasts": [
                    {
                        "ok": True,
                        "time_utc": "2020-04-13T03:00:00Z",
                        "temperature_celcius": 15.79,
                        "forecast_age_hours": 1,
                        "forecast_issue_time": "2020-04-12T12:00Z"
                    },
                    {
                        "ok": True,
                        "time_utc": "2020-04-13T03:00:00Z",
                        "temperature_celcius": 15.84,
                        "forecast_age_hours": 3,
                        "forecast_issue_time": "2020-04-12T12:00Z"
                    },
                ]
            }
        """
        forecast_object = {"services": [], "forecasts": []}

        for service in self.services:
            try:
                response = service.retrieve(self.location_object, self.local_date)
                forecast_object["services"].append(service.__name__)
                response["service"] = service.__name__
                forecast_object["forecasts"].append(response)
            except OutOfRange as e:
                print(f"OutOfRange exception")
                print(e)
                response = {"ok": False}

        return forecast_object

    def _compute_aggregates(self):
        """"""
        agg_object = {}
        temperatures = [
            elt["temperature_celcius"] for elt in self.detailed["forecasts"]
        ]
        agg_object["average"] = round(sum(temperatures) / len(temperatures), 2)
        agg_object["max"] = max(temperatures)
        agg_object["min"] = min(temperatures)

        return agg_object


if __name__ == "__main__":
    from pyweather.forecast import Forecast
    from pyweather.locations import LOCATIONS
    from pyweather.services import BOM, MET, YRNO, ACCUWEATHER

    from pprint import pprint

    CITIES = ["SYDNEY", "MELBOURNE", "BRISBANE"]
    TOMORROW_1_PM = "2020-04-14T13:00"
    SERVICES = [BOM, YRNO]

    for city in CITIES:
        forecast = Forecast(LOCATIONS[city], TOMORROW_1_PM, services=SERVICES)
        f_avg, f_max, f_min = forecast.aggregated["average"], forecast.aggregated["max"], forecast.aggregated["min"]
        print(f"""Average: {f_avg},    Max: {f_max},    Min: {f_min}""")