from pathlib import Path
import time
import logging
from ..helpers import SQLite, MSSQL, get_config, get_folder_info, get_geotags
from .photo import Photo


class Folder:

    def __init__(self, name):
        self.logger = logging.getLogger(
            str(self.__class__.__name__ + ": " + name))

        self.name = name

        self.thumbnail_size = None

        self.path_photos = Path(get_config("paths")["photos"] + "/" + name)

        self.path_thumbnails = Path(get_config("paths")["photos"] +
                                    "/" + name + "/" + get_config("paths")["thumbnail"])

        self.path_colors = Path(get_config("paths")["photos"] +
                                "/" + name + "/" + get_config("paths")["color"])

        self.title, self.description, self.coordinates = get_folder_info(self.path_photos)
        
        self.country, self.city, self.label = get_geotags(
                self.coordinates, self.logger)

        self.sqlite = SQLite(self.logger)
        self.sqlite.create_table(name)

        if get_config("mssql") is not None:
            self.mssql = MSSQL(self.logger)
            self.mssql.create_table(name)
        else:
            self.mssql = None

        self.add_to_db()
        self.create_folders()
        self.clean_folders()

    def get_list_of_files(self, path):
        """
        Return list of fils from folder
        """
        return [f for f in path.iterdir() if f.is_file() and f.name.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def process_files(self):

        for photo in self.get_list_of_files(self.path_photos):
            p = Photo(photo)
            p.add_to_db()

    def clean_folders(self):

        list_of_photos = self.get_list_of_files(self.path_photos)
        list_of_tum = self.get_list_of_files(self.path_thumbnails)
        list_of_col = self.get_list_of_files(self.path_colors)
        list_of_sqlite = self.sqlite.get_names(self.name)

        for tum in list_of_tum:
            if tum.name not in [src.name for src in list_of_photos]:
                tum.unlink()
                self.logger.info("Deleted thumbnail: " + str(tum))

        for col in list_of_col:
            if col.name not in [src.name for src in list_of_photos]:
                col.unlink()
                self.logger.info("Deleted color: " + str(col))

        for d in list_of_sqlite:
            if d not in [src.name for src in list_of_photos]:
                self.sqlite.delete_photo(d, self.name)

        if self.mssql is not None:
            list_of_mssql = self.mssql.get_names(self.name)
            for d in list_of_mssql:
                if d not in [src.name for src in list_of_photos]:
                    self.mssql.delete_photo(d, self.name)

    def create_folders(self):

        self.path_thumbnails.mkdir(parents=True, exist_ok=True)
        self.path_colors.mkdir(parents=True, exist_ok=True)

        self.logger.info("Subfolders checked.")

    def add_to_db(self):
        sqlite = SQLite(self.logger)
        sqlite.add_folder(self.name, self.title, self.description,
         ', '.join(map(str, self.coordinates)), self.country, self.city, self.label)