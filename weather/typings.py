from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias, Callable
from abc import abstractmethod


@dataclass
class Measurement:
    city: str
    when: datetime
    temp: float
    feels: float


@dataclass
class HistoryCityEntry:
    when: datetime
    temp: float
    feels: float


History: TypeAlias = dict[str, HistoryCityEntry]


@dataclass
class TemperatureDiff:
    when: datetime
    temp: float
    feels: float


LoadCityFunction: TypeAlias = Callable[[str], HistoryCityEntry | None]
LoadSecretFunction: TypeAlias = Callable[[str], str]
MeasureTemperatureFunction: TypeAlias = Callable[[str], Measurement]
SaveCityFunction: TypeAlias = Callable[[str, HistoryCityEntry], None]

class HistoryProvier:
    @abstractmethod
    def load(self, city: str):
        raise NotImplementedError()
    @abstractmethod
    def store(self, city: str, city_measurement: HistoryCityEntry):
        raise NotImplementedError()