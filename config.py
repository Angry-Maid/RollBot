import logging
import os

import yaml


class Config(object):

    def __init__(self):
        settings_files = []
        project_path = os.path.dirname(__file__)
        project_settings_file = os.path.join(project_path, 'config.yaml')
        settings_files.append(project_settings_file)

        self.config = {}
        for sf in settings_files:
            try:
                self.update_from_file(sf)
            except Exception as e:
                logging.error(f"Error while reading config file {sf}: {e}")

    def update(self, dct):
        self.config.update(dct)

    def update_from_file(self, path):
        with open(path, 'r') as custom_config:
            self.config.update(
                yaml.load(custom_config.read())
            )

    def dump(self):
        return yaml.dump(self.config)

    def __getattr__(self, item):
        return self.config.get(item, None)

    def __repr__(self):
        return "<configurations object>"


config = Config()
