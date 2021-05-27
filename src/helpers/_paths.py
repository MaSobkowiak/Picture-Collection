from pathlib import Path
import json
import logging
from ._config import get_config


def get_folders(path=None):
    """ Return list of folders in root directory """

    if path is None:
        path = Path(get_config("paths")["photos"])

    return [folder for folder in path.iterdir() if folder.is_dir()]

def check_if_key_in_dict(dict, key):
    if key in dict:
        return dict[key]
    else:
        if key == 'geoTags':
            return []
        else:
            return None

def get_folder_info(path):
    """ Return dict of info.json in folder directory """

    logger = logging.getLogger(str("Folder: " + path.name))

    try:
        if Path(path, 'info.json').is_file():
            with open(Path(path, 'info.json'), encoding='utf-8') as json_info:
                
                data = json.loads(json_info.read())
                
                return check_if_key_in_dict(data, 'title'), check_if_key_in_dict(data, 'description'),  check_if_key_in_dict(data, 'geoTags')
        else:
            logger.warning("Cant find info.json for folder: " +
                    str(path))
            return None, None, []

    except (OSError, KeyError) as e:
        logger.error("Failed to load info.json file: " +
                     str(path.parent) + " " + str(e))