from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from weather.typings import HistoryCityEntry, LoadCityFunction, SaveCityFunction


class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        elif is_dataclass(o):
            return asdict(o)
        return super().default(o)


def initialize_history_io() -> tuple[LoadCityFunction, SaveCityFunction]:
    history_path = Path("history.json")
    history = None

    def __load_history():
        nonlocal history
        if history is None:
            if history_path.exists():
                with open(history_path, "r", encoding="utf-8") as file:
                    history = json.load(file)
            else:
                history = {}

    def load(city: str) -> HistoryCityEntry | None:
        __load_history()
        record = history.get(city)
        if record is not None:
            return HistoryCityEntry(
                when=datetime.fromisoformat(record["when"]),
                temp=record["temp"],
                feels=record["feels"]
            )

    def store(city: str, city_measurement: HistoryCityEntry):
        __load_history()
        history[city] = city_measurement
        with open(history_path, "w", encoding="utf-8") as file:
            json.dump(history, file, cls=DatetimeJSONEncoder)

    return load, store


def load_secret(name: str) -> str:
    with open("secrets.json", "r", encoding="utf-8") as file:
        return json.load(file)[name]
