from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias


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
