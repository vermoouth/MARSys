from threading import Thread
from datetime import datetime
from time import sleep
from abc import ABC, abstractmethod


class CheckerBase(ABC, Thread):
    """Абстрактный метод для чекеров, наследники обязаны реализовать функцию
    check(), возвращающую логическое значение доступности системы
    """
    last_check_time: datetime
    is_last_check_succeed: bool

    def __init__(self, checking_period: float):
        super().__init__()
        self.is_running: bool = False
        self.checking_period = checking_period

    @property
    @abstractmethod
    def checking_address(self) -> str:
        ...

    @abstractmethod
    def check(self) -> bool:
        """Проверить доступность системы"""

    # def get_status(self):

    def start(self) -> None:
        self.is_last_check_succeed = self.check()
        self.last_check_time = datetime.now()
        self.is_running = True
        super().start()

    def run(self) -> None:
        while self.is_running:
            check_start = datetime.now()
            self.is_last_check_succeed = self.check()
            self.last_check_time = datetime.now()
            elapsed_time = (self.last_check_time - check_start).total_seconds()
            if self.checking_period > elapsed_time:
                sleep(self.checking_period - elapsed_time)

    def stop(self) -> None:
        self.is_running = False
        self.join()
