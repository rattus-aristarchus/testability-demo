from dataclasses import dataclass
from datetime import datetime
import pytest

from weather.app_logic import get_temp_diff, save_measurement
from weather.typings import HistoryCityEntry, Measurement, TemperatureDiff


pytestmark = [pytest.mark.fast]


@pytest.fixture
def measurement():
    yield Measurement(
        city="New York",
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )


def test_get_temp_diff_unknown_city():
    assert get_temp_diff(None, Measurement(
        city="New York",
        when=datetime.now(),
        temp=10,
        feels=10
    )) is None


def test_get_temp_diff_known_city(measurement):
    assert get_temp_diff(
        HistoryCityEntry(
            when=datetime(2023, 1, 1, 0, 0, 0),
            temp=10,
            feels=10,
        ),
        measurement
    ) == TemperatureDiff(
        when=datetime(2023, 1, 1, 0, 0, 0),
        temp=-2,
        feels=2,
    )


@dataclass
class __SaveSpy:
    calls: int = 0
    last_city: str | None = None
    last_entry: HistoryCityEntry | None = None


@pytest.fixture
def save_spy():
    spy = __SaveSpy()
    def __save(city, entry):
        spy.calls += 1
        spy.last_city = city
        spy.last_entry = entry
    yield __save, spy


def test_measurement_with_no_diff_saved(save_spy, measurement):
    save, spy = save_spy

    save_measurement(save, measurement, None)

    assert spy.calls == 1
    assert spy.last_city == "New York"
    assert spy.last_entry == HistoryCityEntry(
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )


def test_measurement_with_recent_diff_not_saved(save_spy, measurement):
    save, spy = save_spy

    # Less than 6 hours have passed
    save_measurement(save, measurement, TemperatureDiff(
        when=datetime(2023, 1, 1, 20, 0, 0),
        temp=10,
        feels=10,
    ))

    assert not spy.calls


def test_measurement_with_old_diff_saved(save_spy, measurement):
    save, spy = save_spy

    # More than 6 hours have passed
    save_measurement(save, measurement, TemperatureDiff(
        when=datetime(2023, 1, 1, 17, 0, 0),
        temp=-2,
        feels=2,
    ))

    assert spy.calls == 1
    assert spy.last_city == "New York"
    assert spy.last_entry == HistoryCityEntry(
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )
