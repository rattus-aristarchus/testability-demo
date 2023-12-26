import pytest
from datetime import datetime
from weather import (
    get_my_ip,
    get_city_by_ip,
    get_temp_diff,
    print_temperature,
    local_weather,
)
from typings import Measurement, HistoryCityEntry, TemperatureDiff
import re
import ipaddress


@pytest.mark.slow
def test_local_weather(capsys: pytest.CaptureFixture):
    local_weather()

    assert re.match(
        (
            r"^Temperature in .*: -?\d+ °C\n"
            r"Feels like -?\d+ °C\n"
            r"Last measurement taken on .*\n"
            r"Difference since then: -?\d+ \(feels -?\d+\)$"
        ),
        capsys.readouterr().out
    )


@pytest.mark.slow
def test_get_my_ip_returns_something():
    # Raises if no a well-formed IP
    ipaddress.ip_address(
        get_my_ip()
    )


@pytest.mark.slow
def test_my_city_returns_something():
    assert get_city_by_ip(
        get_my_ip()
    )


@pytest.mark.slow
def test_city_of_known_ip():
    assert get_city_by_ip("69.193.168.152") == "Astoria"


@pytest.mark.fast
def test_get_temp_diff_unknown_city():
    assert get_temp_diff({}, Measurement(
        city="New York",
        when=datetime.now(),
        temp=10,
        feels=10
    )) is None


@pytest.mark.fast
def test_get_temp_diff_known_city():
    assert get_temp_diff({
        "New York": HistoryCityEntry(
            when=datetime(2023, 1, 1, 0, 0, 0),
            temp=10,
            feels=10,
        )
    }, Measurement(
        city="New York",
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )) == TemperatureDiff(
        when=datetime(2023, 1, 1, 0, 0, 0),
        temp=-2,
        feels=2,
    )


@pytest.mark.fast
def test_print_temperature_without_diff(capsys: pytest.CaptureFixture):
    print_temperature(
        Measurement(
            city="My City",
            when=datetime(2023, 1, 1),
            temp=21.4,
            feels=24.5,
        ),
        None
    )

    assert re.match(
        (
            r"^Temperature in .*: -?\d+ °C\n"
            r"Feels like -?\d+ °C$"
        ),
        capsys.readouterr().out
    )
