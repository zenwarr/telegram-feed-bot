import os
import yaml


def get_config():
    with open(get_config_file_path(), 'r') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


def get_data_dir():
    return os.environ.get("DATA_DIR") or "/data"


def get_config_file_path():
    return os.path.join(get_data_dir(), "config.yaml")
