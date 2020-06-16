from pathlib import Path
import logging
import json


def get_config(key: str):
    """
    Get value from config file.
    Parameters:
        :param str key: Key of the value to get.
    """

    logger = logging.getLogger(__name__.replace(str(__package__) + ".", ''))

    config_path = Path(r"./config.json")

    try:
        if config_path.exists():
            with open(config_path, encoding='utf-8') as json_config:

                config = json.loads(json_config.read())

                if key in config:
                    return config[key]
                else:
                    return None

    except (OSError, KeyError) as e:
        logger.error("Failed to load config file: " +
                     str(config_path) + " " + str(e))
