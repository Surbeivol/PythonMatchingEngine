import os
import os.path
import yaml


class Configuration:
    def __init__(self):
       self.path = os.path.dirname(__file__)

    def get_liq_bands(self):
        return self.__load_config(os.path.join(self.path,'liq_bands.yml'))

    def get_trades_bands(self):
        return self.__load_config(os.path.join(self.path,'trades_bands.yml'))

    def __load_config(self, file_path):
        if not os.path.exists(file_path):
            raise AttributeError(f"Config file not found:{file_path}")

        # TODO: assert with a template
        with open(file_path, 'r')as stream:
            try:
                yaml_conf = yaml.load(stream, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                raise Exception(f'Error loading '
                                f'configuration file {file_path}: {exc}')
        return yaml_conf
