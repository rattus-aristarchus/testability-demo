from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from weather.typings import HistoryCityEntry, HistoryProvider


class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        elif is_dataclass(o):
            return asdict(o)
        return super().default(o)


class FileHistoryProvider(HistoryProvider):
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


def load_secret(name: str) -> str:
    with open("secrets.json", "r", encoding="utf-8") as file:
        return json.load(file)[name]
