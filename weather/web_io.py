from datetime import datetime
import requests

from weather.typings import LoadSecretFunction, MeasureTemperatureFunction, Measurement, TempService


def get_my_ip() -> str:
    url = "https://api64.ipify.org?format=json"
    response = requests.get(url).json()
    return response["ip"]


def get_city_by_ip(ip_address: str) -> str:
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url).json()
    return response["city"]


class Openweathermap(TempService):

    def __init__(self, load_secret: LoadSecretFunction):
        self.api_key = load_secret("openweathermap.org")

    def measure_temperature(self, city: str) -> Measurement:
        url = (
            "https://api.openweathermap.org/data/2.5/weather?q={0}&"
            "units=metric&lang=ru&appid={1}"
        ).format(city, self.api_key)
        weather_data = requests.get(url).json()
        temperature = weather_data["main"]["temp"]
        temperature_feels = weather_data["main"]["feels_like"]
        return Measurement(
            city=city,
            when=datetime.now(),
            temp=temperature,
            feels=temperature_feels
        )
