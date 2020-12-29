from configparser import ConfigParser

from mars.monitor_config import MonitorConfig
from mars.checkers import available_checkers
from mars.config_loaders.config_loader_base import ConfigLoaderBase


class FileConfigLoader(ConfigLoaderBase):
    def __init__(self, config_file):
        self.config = ConfigParser()
        self.config.read(config_file)

    def load_config(self) -> MonitorConfig:
        for checker in available_checkers:
            if checker.__name__ == self.config['Default config']['Default checker']:
                default_checker = checker
        if 'default_checker' not in locals():
            raise Exception('Unknown checker declared in config file')
        return MonitorConfig(
            float(self.config['Default config']['Checkers polling period']),
            default_checker
        )
