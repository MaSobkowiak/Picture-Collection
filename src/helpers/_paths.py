from pathlib import Path
from ._config import get_config


def get_folders(path=None):
    """ Return list of folders in root directory """

    if path is None:
        path = Path(get_config("paths")["photos"])

    return [folder for folder in path.iterdir() if folder.is_dir()]
