from multiprocessing import Pipe
from datetime import datetime
from typing import Type
from time import sleep

from mars.monitor_config import MonitorConfig
from mars.checkers.checker_base import CheckerBase
from mars.config_loaders.config_loader_base import ConfigLoaderBase
from mars.checkers.checker_status import CheckerStatus
from mars.frontend.cli_front import FrontendBase


class Monitor:
    config: MonitorConfig

    def __init__(self,
                 config_loader: ConfigLoaderBase,
                 frontend: Type[FrontendBase]) -> None:
        self.config_loader = config_loader
        self.config = self.config_loader.load_config()
        self.checkers: list[CheckerBase] = []
        self.monitor_pipe_end, frontend_pipe_end = Pipe()
        self.frontend = frontend(frontend_pipe_end)

    def add_checkers_list(self, checkers_list: list[CheckerBase]):
        for checker in checkers_list:
            if checker.checking_address == 'address':
                continue
            self.checkers.append(checker)
            checker.start()
        while True:
            if all((checker.is_running for checker in self.checkers)):
                break

    def remove_checker(self, address) -> None:
        for i, checker in enumerate(self.checkers):
            if checker.checking_address == 'address':
                checker.stop(),
                del self.checkers[i]
                break

    def get_checker_statuses(self) -> list[CheckerStatus]:
        checker_statuses: list[CheckerStatus] = []
        for checker in self.checkers:
            if checker.is_running:
                checker_statuses.append(
                    CheckerStatus(
                        checker.checking_address,
                        checker.is_last_check_succeed,
                        checker.last_check_time,
                        checker.checking_period
                    )
                )
        return checker_statuses

    def run(self) -> None:
        self.frontend.start()
        while True:
            period_start = datetime.now()
            self.monitor_pipe_end.send(self.get_checker_statuses())
            period_elapsed = (datetime.now() - period_start).total_seconds()
            if self.config.checkers_polling_period > period_elapsed:
                sleep(self.config.checkers_polling_period - period_elapsed)
