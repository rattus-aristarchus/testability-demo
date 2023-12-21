from . import app_logic, web_io, file_io, console_io


def local_weather(
    get_my_ip=None,
    get_city_by_ip=None,
    measure_temperature=None,
    load_last_measurement=None,
    save_city_measurement=None,
    show_temperature=None,
):
    # Initialization logic
    default_load_last_measurement, default_save_city_measurement =\
        file_io.initialize_history_io()
    return app_logic.local_weather(
        get_my_ip=get_my_ip or web_io.get_my_ip,
        get_city_by_ip=get_city_by_ip or web_io.get_city_by_ip,
        measure_temperature=measure_temperature or web_io.init_temperature_service(
            file_io.load_secret
        ),
        load_last_measurement=load_last_measurement or default_load_last_measurement,
        save_city_measurement=save_city_measurement or default_save_city_measurement,
        show_temperature=show_temperature or console_io.print_temperature,
    )


__all__ = ["local_weather"]
