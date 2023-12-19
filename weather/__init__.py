from . import app_logic, web_io, file_io, console_io

def local_weather():
    # Initialization logic
    load_last_measurement, save_city_measurement =\
        file_io.initialize_history_io()
    return app_logic.local_weather(
        get_my_ip=web_io.get_my_ip,
        get_city_by_ip=web_io.get_city_by_ip,
        measure_temperature=web_io.init_temperature_service(
            file_io.load_secret
        ),
        load_last_measurement=load_last_measurement,
        save_city_measurement=save_city_measurement,
        show_temperature=console_io.print_temperature,
    )

__all__ = ["local_weather"]