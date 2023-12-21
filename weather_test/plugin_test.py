from datetime import datetime
import ipaddress
import re
import pytest
from weather.console_io import print_temperature
from weather.typings import Measurement

from weather.web_io import get_city_by_ip, get_my_ip


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
