from dataclasses import dataclass
from datetime import datetime


@dataclass()
class CheckerStatus:
    address: str
    is_available: bool
    last_check_time: datetime
    checking_period: float
