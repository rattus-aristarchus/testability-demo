from weather.typings import Measurement, TemperatureDiff


def format_message(measurement: Measurement, diff: TemperatureDiff|None) -> str:
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
    return msg


def print_temperature(measurement: Measurement, diff: TemperatureDiff|None):
    msg = format_message(measurement, diff)
    print(msg)
