import argparse
import logging
from pathlib import Path
from src import get_config, Folder
from src import setup_logging, get_folders, SQLite, MSSQL, backup


def parseInput():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-clear', default=False, action='store_true',
                        help='Leave empty folders in source root')
    parser.add_argument('--thumbnail-size', nargs=1, metavar='<?>', type=int, default=[
                        1000], help='Size of the thumbnail (default is 1000 pixels on shorter side)')
    parser.add_argument('--log', nargs=1, metavar='<N>', type=int,
                        default=[1], help='Log level: 1-None, 2-Errors, 3-Full')

    # parser.set_defaults(clear='clear_true')
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging(level=logging.INFO)

    sqlite = SQLite(logging.getLogger("main"))

    sqlite.create_folders_table()

    for db_folder in sqlite.get_tables():
        if db_folder not in [f.name for f in get_folders()]:
            sqlite.delete_table(db_folder)
            sqlite.delete_folder(db_folder)

    if get_config("mssql") is not None:
        mssql = MSSQL(logging.getLogger("main"))

        for mssql_folder in mssql.get_tables():
            if mssql_folder not in [f.name for f in get_folders()]:
                mssql.delete_table(db_folder)

    for f in get_folders():
        folder = Folder(f.name)
        folder.process_files()

    for b in get_config("paths")["backups"]:
        Path(b).mkdir(parents=True, exist_ok=True)
        backup(Path(get_config("paths")["photos"]), Path(b))
