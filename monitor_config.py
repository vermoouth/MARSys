from dataclasses import dataclass
from typing import Type
from mars.checkers.checker_base import CheckerBase


@dataclass
class MonitorConfig:
    checkers_polling_period: float
    default_checker: Type[CheckerBase]

