import os
import os.path
import yaml

class Configuration(object):

    def __init__(self, file_path):
        self.config = self.__load_config(file_path)

    def __load_config(self, file_path):
        if not os.path.exists(file_path):
            raise AttributeError(f"Config file not found:{file_path}")

        # TODO: assert with a template
        with open(file_path, 'r') as stream:
            try:
                yaml_conf = yaml.load(stream, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                raise Exception(f'Error loading '
                                f'configuration file {file_path}: {exc}')
        return yaml_conf
