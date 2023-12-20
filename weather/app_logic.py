from datetime import timedelta
from weather.typings import (
    Measurement,
    TemperatureDiff,
    HistoryCityEntry,
)

import weather.console_io as console_io
import weather.file_io as file_io
import weather.web_io as web_io
from weather.typings import HistoryProvier


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
    historyProvider: HistoryProvier,
    measurement: Measurement,
    diff: TemperatureDiff|None
):
    if diff is None or (measurement.when - diff.when) > timedelta(hours=6):
        new_record = HistoryCityEntry(
            when=measurement.when,
            temp=measurement.temp,
            feels=measurement.feels
        )
        historyProvider.store(measurement.city, new_record)


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
    historyProvider = file_io.FileHistoryProvider()
    #load_last_measurement, save_city_measurement =\
    #    file_io.initialize_history_io()

    last_measurement = historyProvider.load(city) # IO

    diff = get_temp_diff(last_measurement, measurement) # App
    save_measurement(historyProvider, measurement, diff) # App

    console_io.print_temperature(measurement, diff) # IO