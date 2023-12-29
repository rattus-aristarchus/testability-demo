from datetime import timedelta
from weather.typings import (
    Measurement,
    TemperatureDiff,
    SaveCityFunction,
    HistoryCityEntry,
)

import weather.console_io as console_io
import weather.file_io as file_io
import weather.web_io as web_io


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
    save_city: SaveCityFunction,
    measurement: Measurement,
    diff: TemperatureDiff|None
):
    """
    If enough time has passed since last measurement, save measurement.
    """
    if diff is None or (measurement.when - diff.when) > timedelta(hours=6):
        new_record = HistoryCityEntry(
            when=measurement.when,
            temp=measurement.temp,
            feels=measurement.feels
        )
        save_city(measurement.city, new_record)


def local_weather():
    # App logic (Use Case)
    # Still has low-level dependencies
    # Additionally has new initialization logic
    # Still untestable

    ip_address = web_io.get_my_ip() # IO
    city = web_io.get_city_by_ip(ip_address) # IO

    # Initialization
    measure_temperature = web_io.init_temperature_service(file_io.load_secret)

    measurement = measure_temperature(city) # IO

    # Initialization
    load_last_measurement, save_city_measurement =\
        file_io.initialize_history_io()

    last_measurement = load_last_measurement(city) # IO

    diff = get_temp_diff(last_measurement, measurement) # App
    save_measurement(save_city_measurement, measurement, diff) # App

    console_io.print_temperature(measurement, diff) # IO