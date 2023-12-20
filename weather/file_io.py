from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from weather.typings import HistoryCityEntry, LoadCityFunction, SaveCityFunction, HistoryProvier

class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        elif is_dataclass(o):
            return asdict(o)
        return super().default(o)


class FileHistoryProvider(HistoryProvier):
    def __init__(self):
        self.__path = Path("history.json")
        self.__history = None

    def load(self, city: str) -> HistoryCityEntry | None:
        self.__load_history()
        record = self.__history.get(city)
        if record is not None:
            return HistoryCityEntry(
                when=datetime.fromisoformat(record["when"]),
                temp=record["temp"],
                feels=record["feels"]
            )

    def store(self, city: str, city_measurement: HistoryCityEntry):
        self.__load_history()
        self.__history[city] = city_measurement
        with open(self.__path, "w", encoding="utf-8") as file:
            json.dump(self.__history, file, cls=DatetimeJSONEncoder)

    def __load_history(self):
        if self.__history is None:
            if self.__path.exists():
                with open(self.__path, "r", encoding="utf-8") as file:
                    self.__history = json.load(file)
            else:
                self.__history = {}

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
