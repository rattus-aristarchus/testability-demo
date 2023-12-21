import json
import requests
from pathlib import Path
from datetime import datetime, timedelta


def local_weather():
    # First, get the IP
    url = "https://api64.ipify.org?format=json"
    response = requests.get(url).json()
    ip_address = response["ip"]

    # Using the IP, determine the city
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url).json()
    city = response["city"]

    with open("secrets.json", "r", encoding="utf-8") as file:
        owm_api_key = json.load(file)["openweathermap.org"]

    # Hit up a weather service for weather in that city
    url = (
        "https://api.openweathermap.org/data/2.5/weather?q={0}&"
        "units=metric&lang=ru&appid={1}"
    ).format(city, owm_api_key)
    weather_data = requests.get(url).json()
    temperature = weather_data["main"]["temp"]
    temperature_feels = weather_data["main"]["feels_like"]

    # If past measurements have already been taken, compare them to current results
    has_previous = False
    history = {}
    history_path = Path("history.json")
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as file:
            history = json.load(file)
        record = history.get(city)
        if record is not None:
            has_previous = True
            last_date = datetime.fromisoformat(record["when"])
            last_temp = record["temp"]
            last_feels = record["feels"]
            diff = temperature - last_temp
            diff_feels = temperature_feels - last_feels

    # Write down the current result if enough time has passed
    now = datetime.now()
    if not has_previous or (now - last_date) > timedelta(hours=6):
        record = {
            "when": datetime.now().isoformat(),
            "temp": temperature,
            "feels": temperature_feels
        }
        history[city] = record
        with open(history_path, "w", encoding="utf-8") as file:
            json.dump(history, file)

    # Print the result
    msg = (
        f"Temperature in {city}: {temperature:.0f} °C\n"
        f"Feels like {temperature_feels:.0f} °C"
    )
    if has_previous:
        formatted_date = last_date.strftime("%c")
        msg += (
            f"\nLast measurement taken on {formatted_date}\n"
            f"Difference since then: {diff:.0f} (feels {diff_feels:.0f})"
        )
    print(msg)


if __name__ == "__main__":
    local_weather()
