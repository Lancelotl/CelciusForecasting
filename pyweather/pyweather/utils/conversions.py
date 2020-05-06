from decimal import Decimal


def farenheit_to_celcius(temperature):
    """Converts a farenheit temperature to celcius
    """
    temperature = str(temperature)
    return (Decimal(temperature) - Decimal("32")) * (Decimal("5") / Decimal("9"))


def celcius_to_farenheit(temperature):
    """Converts a celcius temperature to farenheit
    """
    temperature = str(temperature)
    return (Decimal(temperature) * (Decimal("9") / Decimal("5"))) + Decimal("32")