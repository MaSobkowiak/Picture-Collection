from pathlib import Path
import time
import logging
from ..helpers import Database, get_config
from .photo import Photo


class Folder:

    def __init__(self, name):
        self.logger = logging.getLogger(
            str(self.__class__.__name__ + ": " + name))

        self.name = name
        self.db = Database(self.logger)
        self.thumbnail_size = None

        self.path_photos = Path(get_config("paths")["photos"] + "/" + name)

        self.path_thumbnails = Path(get_config("paths")["photos"] +
                                    "/" + name + "/" + get_config("paths")["thumbnail"])

        self.path_colors = Path(get_config("paths")["photos"] +
                                "/" + name + "/" + get_config("paths")["color"])

        self.db.create_table(name)
        self.create_folders()

        self.clean_folders()

    def get_list_of_files(self, path):
        """
        Return list of fils from folder
        """
        return ([photo for photo in path.iterdir() if photo.is_file()])

    def process_files(self):

        for photo in self.get_list_of_files(self.path_photos):
            p = Photo(photo)
            p.add_to_db()

    def clean_folders(self):

        list_of_photos = self.get_list_of_files(self.path_photos)
        list_of_tum = self.get_list_of_files(self.path_thumbnails)
        list_of_col = self.get_list_of_files(self.path_colors)
        list_of_db = self.db.get_names(self.name)

        for tum in list_of_tum:
            if tum.name not in [src.name for src in list_of_photos]:
                tum.unlink()
                self.logger.info("Deleted thumbnail: " + str(tum))

        for col in list_of_col:
            if col.name not in [src.name for src in list_of_photos]:
                col.unlink()
                self.logger.info("Deleted color: " + str(col))

        for d in list_of_db:
            if d not in [src.name for src in list_of_photos]:
                self.db.delete_photo(d, self.name)

    def create_folders(self):

        self.path_thumbnails.mkdir(parents=True, exist_ok=True)
        self.path_colors.mkdir(parents=True, exist_ok=True)

        self.logger.info("Subfolders checked.")
