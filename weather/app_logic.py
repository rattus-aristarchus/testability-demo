from datetime import timedelta
from weather.typings import (
    GetCityFunction,
    GetIPFunction,
    Measurement,
    ShowTemperatureFunction,
    TemperatureDiff,
    HistoryCityEntry,
    HistoryProvider,
    TempService
)


def get_temp_diff(
    last_measurement: HistoryCityEntry | None,
    new_measurement: Measurement
) -> TemperatureDiff|None:
    if last_measurement is not None:
        return TemperatureDiff(
            when=last_measurement.when,
            temp=new_measurement.temp - last_measurement.temp,
            feels=new_measurement.feels - last_measurement.feels
        )


def save_measurement(
    history_provider: HistoryProvider,
    measurement: Measurement,
    diff: TemperatureDiff|None
):
    if diff is None or (measurement.when - diff.when) > timedelta(hours=6):
        new_record = HistoryCityEntry(
            when=measurement.when,
            temp=measurement.temp,
            feels=measurement.feels
        )
        history_provider.store(measurement.city, new_record)


def local_weather(
    get_my_ip: GetIPFunction,
    get_city_by_ip: GetCityFunction,
    show_temperature: ShowTemperatureFunction,
    temp_service: TempService,
    history_provider: HistoryProvider
):
    # App logic (Use Case)
    # Low-level dependencies are injected at runtime
    # Initialization logic is in __init__.py now
    # Can be tested with dummies, stubs and spies!

    ip_address = get_my_ip() # injected IO
    city = get_city_by_ip(ip_address) # injected IO
    if city is None:
        raise ValueError("Cannot determine the city")
    measurement = temp_service.measure_temperature(city) # injected IO
    last_measurement = history_provider.load(city) # injected IO
    diff = get_temp_diff(last_measurement, measurement) # App
    save_measurement(history_provider, measurement, diff) # App (with injected IO)
    show_temperature(measurement, diff) # injected IO
