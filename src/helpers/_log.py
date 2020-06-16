import logging
import logging.config
from pathlib import Path
import json
from datetime import datetime


def setup_logging(config_path=Path('./logging.json'), level=None):
    """
    Setup logging configuration.
    Parameters:
        :param str config_path: path to the logging json config file.
        :param str level: level of logging.
    """

    if config_path.exists():
        with open(config_path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)

    if level is not None:
        logging.getLogger().setLevel(level)
    else:
        logging.getLogger().setLevel(logging.INFO)
