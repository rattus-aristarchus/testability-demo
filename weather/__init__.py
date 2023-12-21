from . import app_logic, web_io, file_io, console_io


def local_weather(
    get_my_ip=None,
    get_city_by_ip=None,
    show_temperature=None,
    history_provider=None,
    temp_service=None
):
    # Initialization logic
    file_history_provider = file_io.FileHistoryProvider()
    openweathermap = web_io.Openweathermap(file_io.load_secret)
    return app_logic.local_weather(
        get_my_ip=get_my_ip or web_io.get_my_ip,
        get_city_by_ip=get_city_by_ip or web_io.get_city_by_ip,
        show_temperature=show_temperature or console_io.print_temperature,
        history_provider=history_provider or file_history_provider,
        temp_service=temp_service or openweathermap
    )


__all__ = ["local_weather"]
