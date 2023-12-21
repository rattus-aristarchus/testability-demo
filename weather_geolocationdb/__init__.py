import requests


def get_city_by_ip(ip: str):
    """Get user's city based on their IP"""

    url = f"https://geolocation-db.com/json/{ip}?position=true"
    response = requests.get(url).json()
    return response["city"]


__all__ = ["get_city_by_ip"]
