import json
import os


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self, config_path='config.json'):
        with open(config_path, 'r') as config_file:
            self._config = json.load(config_file)

    def get(self, key, default=None):
        return self._config.get(key, default)

    @property
    def window_size(self):
        return self._config.get("window_size", 1)

    @property
    def desired_frequency(self):
        return self._config.get("desired_frequency", 25)

    @property
    def max_depth(self):
        return self._config.get("max_depth", 1)