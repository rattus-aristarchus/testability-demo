import json
from typing import Any
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import is_dataclass, asdict

from typings import Measurement, HistoryCityEntry, History, TemperatureDiff


# IO logic: save history of measurements
class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        elif is_dataclass(o):
            return asdict(o)
        return super().default(o)


def get_my_ip() -> str:
    # IO: load IP from HTTP service
    url = "https://api64.ipify.org?format=json"
    response = requests.get(url).json()
    return response["ip"]


def get_city_by_ip(ip_address: str) -> str:
    # IO: load city by IP from HTTP service
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url).json()
    return response["city"]


def measure_temperature(city: str) -> Measurement:
    # IO: Load API key from file
    with open("secrets.json", "r", encoding="utf-8") as file:
        owm_api_key = json.load(file)["openweathermap.org"]

    # IO: load measurement from weather service
    url = (
        "https://api.openweathermap.org/data/2.5/weather?q={0}&"
        "units=metric&lang=ru&appid={1}"
    ).format(city, owm_api_key)
    weather_data = requests.get(url).json()
    temperature = weather_data["main"]["temp"]
    temperature_feels = weather_data["main"]["feels_like"]
    return Measurement(
        city=city,
        when=datetime.now(),
        temp=temperature,
        feels=temperature_feels
    )


def load_history() -> History:
    # IO: load history from file
    history_path = Path("history.json")
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as file:
            history_by_city = json.load(file)
            return {
                city: HistoryCityEntry(
                    when=datetime.fromisoformat(record["when"]),
                    temp=record["temp"],
                    feels=record["feels"]
                ) for city, record in history_by_city.items()
            }
    return {}


def get_temp_diff(history: History, measurement: Measurement) -> TemperatureDiff|None:
    # App logic: calculate temperature difference
    entry = history.get(measurement.city)
    if entry is not None:
        return TemperatureDiff(
            when=entry.when,
            temp=measurement.temp - entry.temp,
            feels=measurement.feels - entry.feels
        )


def save_measurement(history: History, measurement: Measurement, diff: TemperatureDiff|None):
    # App logic: check if should save the measurement
    if diff is None or (measurement.when - diff.when) > timedelta(hours=6):
        # IO: save new measurement to file
        new_record = HistoryCityEntry(
            when=measurement.when,
            temp=measurement.temp,
            feels=measurement.feels
        )
        history[measurement.city] = new_record
        history_path = Path("history.json")
        with open(history_path, "w", encoding="utf-8") as file:
            json.dump(history, file, cls=DatetimeJSONEncoder)


def print_temperature(measurement: Measurement, diff: TemperatureDiff|None):
    # IO: format and print message to user
    msg = (
        f"Temperature in {measurement.city}: {measurement.temp:.0f} °C\n"
        f"Feels like {measurement.feels:.0f} °C"
    )
    if diff is not None:
        last_measurement_time = diff.when.strftime("%c")
        msg += (
            f"\nLast measurement taken on {last_measurement_time}\n"
            f"Difference since then: {diff.temp:.0f} (feels {diff.feels:.0f})"
        )
    print(msg)


def local_weather():
    # App logic (Use Case)
    ip_address = get_my_ip() # IO
    city = get_city_by_ip(ip_address) # IO
    measurement = measure_temperature(city) # IO
    history = load_history() # IO
    diff = get_temp_diff(history, measurement) # App
    save_measurement(history, measurement, diff) # App, IO
    print_temperature(measurement, diff) # IO


if __name__ == "__main__":
    local_weather()
