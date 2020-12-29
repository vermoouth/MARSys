from multiprocessing.connection import Connection
from multiprocessing import Process
from abc import ABC


class FrontendBase(ABC, Process):
    def __init__(self, out_pipe: Connection):
        super().__init__()
        self.frontend_pipe: Connection = out_pipe




