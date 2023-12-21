from . import app_logic


def local_weather():
    return app_logic.local_weather()


__all__ = ["local_weather"]
