from shutil import copy2, rmtree
from pathlib import Path
import logging


def backup(src, dst):
    logger = logging.getLogger("Backup: " + str(dst.name))

    # remove files from backup
    for f in dst.iterdir():
        if f.name not in [s.name for s in src.iterdir()]:
            if f.is_dir():
                rmtree(f)
                logger.info("Removed folder from backup: " + str(f))
            elif f.is_file():
                f.unlink()
                logger.info("Removed file from backup: " + str(f))

    for file_or_dir in src.iterdir():

        if file_or_dir.is_dir():

            from_dir = file_or_dir
            to_dir = Path(dst, file_or_dir.name)

            if not to_dir.exists():
                to_dir.mkdir()
                logger.info("Created folder in backup: " + str(to_dir))

            backup(from_dir, to_dir)

        else:

            from_file = file_or_dir
            to_file = Path(dst, file_or_dir.name)

            if to_file.exists():

                modified_from = from_file.stat().st_mtime
                modified_to = to_file.stat().st_mtime

                if (modified_from > modified_to):

                    to_file.unlink()
                    copy2(from_file, to_file)
                    logger.info("Updated file in backup: " + str(to_file))

            else:
                copy2(from_file, to_file)
                logger.info("Copied file to backup: " + str(to_file))
