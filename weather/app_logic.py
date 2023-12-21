from datetime import timedelta
from weather.typings import (
    Measurement,
    TemperatureDiff,
    HistoryCityEntry,
)

import weather.console_io as console_io
import weather.file_io as file_io
import weather.web_io as web_io
from weather.typings import HistoryProvider


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


def local_weather():
    # App logic (Use Case)
    # Still has low-level dependencies
    # Additionally has new initialization logic
    # Still untestable

    ip_address = web_io.get_my_ip() # IO
    city = web_io.get_city_by_ip(ip_address) # IO

    # Initialization
    weather_service = web_io.Openweathermap(file_io.load_secret)

    measurement = weather_service.measure_temperature(city) # IO

    # Initialization
    history_provider = file_io.FileHistoryProvider()

    last_measurement = history_provider.load(city) # IO

    diff = get_temp_diff(last_measurement, measurement) # App
    save_measurement(history_provider, measurement, diff) # App

    console_io.print_temperature(measurement, diff) # IO
