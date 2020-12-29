from multiprocessing.connection import Connection
from sys import stdout
from os import get_terminal_size
from platform import system
from datetime import datetime
import ctypes

from mars.frontend.frontend_base import FrontendBase
from mars.checkers.checker_status import CheckerStatus


class CLIFrontend(FrontendBase):
    _is_running: bool
    last_checkers_statuses: list
    column_titles = (
        'System',
        'Status',
        'Next check progress',
        'Last check',
        'Checking period'
    )
    column_lengths: list

    def __init__(self, frontend_pipe_end: Connection):
        super().__init__(frontend_pipe_end)
        if system().lower() == 'windows':
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        self.frontend_pipe_end = frontend_pipe_end

    def draw_window(self):
        columns, lines = get_terminal_size()
        stdout.write(f'\u001b[{lines + 1}F[\u001b[0J')
        self.draw_status()
        self.draw_titles(columns)
        self.draw_checkers(lines)

    def draw_status(self):
        status_string = '\n\n' + self.apply_ansi('Online', '32;1m') + ' / ' + \
                        self.apply_ansi('Total', '36;1m') + ' : ' + \
                        self.apply_ansi(
                            f'{len(tuple(checker for checker in self.last_checkers_statuses if checker.is_available))}',
                            '32;1m') + ' / ' + \
                        self.apply_ansi(f'{len(self.last_checkers_statuses)}',
                                        '36;1m') + '\n\n'
        stdout.write(status_string)

    def draw_titles(self, columns):
        self.column_lengths = [
            max((len((self.column_titles[0])),
                 *(len(checker.address) for checker in
                   self.last_checkers_statuses))) + 1,
            10,
            0,
            len(self.column_titles[3]) + 1,
            len(self.column_titles[4]) + 1,
        ]
        self.column_lengths[2] = columns - sum(self.column_lengths)
        titles_string = ''
        for i, column in enumerate(self.column_titles):
            titles_string += column + ' ' * (self.column_lengths[i] - len(column))
        stdout.write(self.apply_ansi(titles_string, '30;43m'))

    def draw_checkers(self, lines):
        for checker in self.last_checkers_statuses:
            table_row = f'{checker.address}' + ' ' * (
                    self.column_lengths[0] - len(f'{checker.address}')) + \
                        (self.apply_ansi('[ONLINE]', '92m') + ' ' * (
                                self.column_lengths[1] - len('[ONLINE]'))
                         if checker.is_available else '[OFFLINE]' + ' ' * (
                                self.column_lengths[1] - len('[OFFLINE]'))) + \
                        self.get_progress_bar(self.column_lengths[2], (
                                datetime.now() - checker.last_check_time).total_seconds() / checker.checking_period * 100) + \
                        checker.last_check_time.strftime('%H:%M:%S') + ' ' * (
                                self.column_lengths[3] - len(
                            checker.last_check_time.strftime('%H:%M:%S'))) + \
                        f'{checker.checking_period} s' + ' ' * (
                                self.column_lengths[4] - len(
                            f'{checker.checking_period} s')) + '\n'
            if not checker.is_available:
                table_row = self.apply_ansi(table_row, '93;41m')
            stdout.write(table_row)
        if len(self.last_checkers_statuses) < lines - 7:
            stdout.write('\n' * ((lines - 7) - len(self.last_checkers_statuses)))

    @staticmethod
    def apply_ansi(text, ansi_codes: str):
        return f'\u001b[{ansi_codes}{text}\u001b[0m'

    @staticmethod
    def get_progress_bar(bar_length, percentage):
        blocks = ('▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
        if bar_length < 3:
            return '-' * bar_length
        if percentage < 0 or percentage > 100:
            return ' ' * bar_length
        blocks_split_float = str(bar_length / 100 * percentage).split('.')
        full_blocks = int(blocks_split_float[0])
        closing_block = blocks[int(8 * float('0.' + blocks_split_float[1]))]
        return f'{blocks[7] * full_blocks}{closing_block}' \
               f'{" " * (bar_length - (full_blocks + 1))}'

    def run(self):
        self._is_running = True
        while self._is_running:
            if self.frontend_pipe_end.poll(timeout=0.05):
                received_data = self.frontend_pipe_end.recv()
                if not all((isinstance(checker, CheckerStatus)
                            for checker in received_data)):
                    continue
                self.last_checkers_statuses = received_data
            self.draw_window()
