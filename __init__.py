import os

APP_NAME = os.path.basename(os.path.dirname(__file__))

__version_info__ = (1, 0, 0)
__version__ = ".".join(map(str, __version_info__))

default_app_config = 'csv_manager.apps.CsvManagerConfig'