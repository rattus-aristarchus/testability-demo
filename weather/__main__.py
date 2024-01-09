from . import local_weather
import weather_geolocationdb


local_weather(get_city_by_ip=weather_geolocationdb.get_city_by_ip)
