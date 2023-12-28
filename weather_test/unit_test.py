from dataclasses import dataclass
from datetime import datetime

import allure
import pytest

from weather.app_logic import get_temp_diff, save_measurement, local_weather
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


def test_city_by_current_ip_is_requested():
    def get_ip_stub(): return "1.2.3.4"
    captured_ip = None

    def get_city_spy(ip):
        nonlocal captured_ip
        captured_ip = ip
        raise ValueError()

    def dummy(*_): raise NotImplementedError()

    with pytest.raises(ValueError):
        local_weather(get_ip_stub, get_city_spy, dummy, dummy, dummy, dummy)

    assert captured_ip == "1.2.3.4"


def test_temperature_of_current_city_is_requested():
    """Make sure that local_weather uses the correct city"""
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return "New York"
    captured_city = None

    def measure_temperature(city):
        nonlocal captured_city
        captured_city = city
        # Execution of local_weather will stop here
        raise ValueError()

    def dummy(*_): raise NotImplementedError()

    # We don't care about most of local_weather's execution,
    # so we can pass dummies that will never be called
    with pytest.raises(ValueError):
        local_weather(
            get_ip_stub,
            get_city_stub,
            measure_temperature,
            dummy,
            dummy,
            dummy
        )

    assert captured_city == "New York"


@allure.title("Use case should save measurement if no previous entries exist")
def test_new_measurement_is_saved(measurement):
    # We don't care about this value:
    def get_ip_stub(): return "1.2.3.4"
    # Nor this:
    def get_city_stub(*_): return "Not used"
    # This is the thing we'll check for:
    def measure_temperature(*_): return measurement
    # With this, local_weather will think there is
    # no last measurement on disk:
    def last_measurement_stub(*_): return None

    captured_city = None
    captured_entry = None

    # This spy will see what local_weather tries to
    # write to disk:
    def save_measurement_spy(city, entry):
        nonlocal captured_city
        nonlocal captured_entry
        captured_city = city
        captured_entry = entry

    def show_temperature_stub(*_): pass

    local_weather(
        get_ip_stub,
        get_city_stub,
        measure_temperature,
        last_measurement_stub,
        save_measurement_spy,
        show_temperature_stub,
    )

    assert captured_city == "New York"
    assert captured_entry == HistoryCityEntry(
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )


@allure.title("Use case should not save measurement if a recent entry exists")
def test_recent_measurement_is_not_saved(measurement):
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return "Not used"
    def measure_temperature(*_): return measurement

    def last_measurement_stub(*_): return HistoryCityEntry(
        datetime(2023, 1, 1, 20, 0, 0),
        temp=10,
        feels=10,
    )
    called = False

    def save_measurement_spy(*_):
        nonlocal called
        called = True

    def show_temperature_stub(*_): pass

    local_weather(
        get_ip_stub,
        get_city_stub,
        measure_temperature,
        last_measurement_stub,
        save_measurement_spy,
        show_temperature_stub,
    )

    assert not called


def test_old_measurement_is_overwritten(measurement):
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return "Not used"
    def measure_temperature(*_): return measurement

    def last_measurement_stub(*_): return HistoryCityEntry(
        datetime(2023, 1, 1, 17, 0, 0),
        temp=10,
        feels=10,
    )
    captured_city = None
    captured_entry = None

    def save_measurement_spy(city, entry):
        nonlocal captured_city
        nonlocal captured_entry
        captured_city = city
        captured_entry = entry

    def show_temperature_stub(*_): pass

    local_weather(
        get_ip_stub,
        get_city_stub,
        measure_temperature,
        last_measurement_stub,
        save_measurement_spy,
        show_temperature_stub,
    )

    assert captured_city == "New York"
    assert captured_entry == HistoryCityEntry(
        when=datetime(2023, 1, 2, 0, 0, 0),
        temp=8,
        feels=12,
    )


def test_measurement_without_diff_is_shown(measurement):
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return "Not used"
    def measure_temperature(*_): return measurement
    def last_measurement_stub(*_): return None
    def save_measurement_stub(*_): pass
    captured_measurement = None
    captured_diff = None

    def show_temperature_spy(measurement, diff):
        nonlocal captured_measurement
        nonlocal captured_diff
        captured_measurement = measurement
        captured_diff = diff

    local_weather(
        get_ip_stub,
        get_city_stub,
        measure_temperature,
        last_measurement_stub,
        save_measurement_stub,
        show_temperature_spy,
    )

    assert captured_measurement == measurement
    assert captured_diff is None


def test_measurement_with_diff_is_shown(measurement):
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return "Not used"
    def measure_temperature(*_): return measurement

    def last_measurement_stub(*_): return HistoryCityEntry(
        when=datetime(2023, 1, 1, 20, 0, 0),
        temp=10,
        feels=10,
    )
    def save_measurement_stub(*_): pass
    captured_measurement = None
    captured_diff = None

    def show_temperature_spy(measurement, diff):
        nonlocal captured_measurement
        nonlocal captured_diff
        captured_measurement = measurement
        captured_diff = diff

    local_weather(
        get_ip_stub,
        get_city_stub,
        measure_temperature,
        last_measurement_stub,
        save_measurement_stub,
        show_temperature_spy,
    )

    assert captured_measurement == measurement
    assert captured_diff == TemperatureDiff(
        when=datetime(2023, 1, 1, 20, 0, 0),
        temp=-2,
        feels=2,
    )


def test_app_crash_if_no_city(measurement):
    def get_ip_stub(): return "1.2.3.4"
    def get_city_stub(*_): return None
    def dummy(*_): raise NotImplementedError()

    with pytest.raises(ValueError) as e:
        local_weather(
            get_ip_stub,
            get_city_stub,
            dummy,
            dummy,
            dummy,
            dummy,
        )

    assert str(e.value) == "Cannot determine the city"
