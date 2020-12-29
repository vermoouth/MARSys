from abc import ABC, abstractmethod
from mars.monitor_config import MonitorConfig


class ConfigLoaderBase(ABC):
    @abstractmethod
    def load_config(self) -> MonitorConfig:
        """Загрузить конфигурацию монитора"""
