import pytest
from weather import local_weather
import re


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
