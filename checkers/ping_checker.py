from platform import system
from subprocess import run, DEVNULL

from mars.checkers.checker_base import CheckerBase


class PingChecker(CheckerBase):
    """Чекер на основе команды ping под Windows и Linux"""
    def __init__(self,
                 address: str,
                 checking_period: float = 5,
                 timeout_seconds: float = None) -> None:
        super().__init__(checking_period)
        self.address = address

        if system().lower() == 'windows':
            params = ['-n', '1']
            if timeout_seconds is not None:
                params.extend(('-w', str(timeout_seconds * 10000)))
        else:
            params = ['-c', '1']
            if timeout_seconds is not None:
                params.extend(('-W', str(timeout_seconds)))
        self.command = ['ping', *params, address]

    @property
    def checking_address(self):
        return self.address

    def check(self) -> bool:
        return run(self.command, stdout=DEVNULL).returncode == 0
