import sqlite3
from sqlite3 import Error
import logging
from ._config import get_config
from pathlib import Path


class SQLite:
    """Class for db"""

    def __init__(self, logger):

        self.logger = logger
        self.connection = self.create_connection()

    def create_connection(self):
        """
        Create a database connection to a SQLite database
        """

        try:
            if get_config("sqlite") is not None:
                conn = sqlite3.connect(str(
                    Path(get_config("sqlite")["path"])), isolation_level=None)
            else:
                conn = sqlite3.connect(str(
                    Path(get_config("paths")["photos"], "pictures.db")), isolation_level=None)

            self.logger.info("Connected to db version: " +
                             sqlite3.version + ".")
            return conn

        except sqlite3.Error as e:
            self.logger.error("Cant connect to db: " + str(e))

    def create_table(self, folder: str):
        """ create a table from the create_table_sql statement """

        sql = """CREATE TABLE IF NOT EXISTS '{0}' (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                path_src text NOT NULL,
                                path_tum text NOT NULL,
                                path_col text NOT NULL,
                                width_src int NOT NULL,
                                height_src int NOT NULL,
                                width_tum int NOT NULL,
                                height_tum int NOT NULL,
                                year integer NOT NULL,
                                month integer NOT NULL,
                                day integer NOT NULL,
                                color real,
                                coordinates text,
                                country text,
                                city text,
                                label text
                                );""".format(folder)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            self.logger.info("Table in db checked.")
        except sqlite3.Error as e:
            self.logger.error("Can't create table: " + str(e))

    def get_names(self, folder):

        sql = """SELECT name FROM '{0}'""".format(folder)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            rows = c.fetchall()

            self.logger.info("Recived names for " + str(folder) + " folder.")

            return [row[0] for row in rows]

        except sqlite3.Error as e:
            self.logger.error("Cant get names for " +
                              str(folder) + " folder from db: " + str(e))

    def check_if_photo_exists(self, name, folder):

        sql = """SELECT * FROM '{0}' WHERE name='{1}' """.format(folder, name)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            rows = c.fetchall()
            if rows:
                return True
            else:
                return False

        except Error as e:
            self.logger.error("Error checking db: " + str(e))

    def add_photo(self, name, path_src, path_tum, path_col, width_src, height_src, width_tum, height_tum, year, month, day, color, coordinates, country, city, label, folder):
        """ Create new photo entry. Params: Photo object, folder name that foto is in"""

        photo_text = (name, path_src, path_tum, path_col, width_src, height_src, width_tum,
                      height_tum, year, month, day, color, coordinates, country, city, label)

        sql = """ INSERT INTO '{0}'(name, path_src, path_tum, path_col,
                                     width_src, height_src, width_tum, height_tum,
                                      year, month, day,
                                      color, coordinates, country, city, label)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """.format(folder)

        try:
            if not self.check_if_photo_exists(name, folder):
                c = self.connection.cursor()
                c.execute(sql, photo_text)
                self.logger.info("Added photo to db: " + str(name))
            else:
                self.logger.info("Photo exists in db: " + str(name))
        except Error as e:
            self.logger.error("Cant add photo: " + str(e))

    def delete_photo(self, name, folder):
        """ Delete photo from db by name"""

        sql = """ DELETE FROM '{0}' WHERE name = '{1}' """.format(folder, name)

        try:
            if self.check_if_photo_exists(name, folder):
                c = self.connection.cursor()
                c.execute(sql)
                self.logger.info(
                    "Deleted photo from db, no longer exists as file")
            else:
                self.logger.info("Can't delete photo, don't exists in db")
        except Error as e:
            self.logger.error("Cant delete photo from db: " + str(e))

    def delete_table(self, folder):
        """ Delete table from db """

        sql = """DROP TABLE '{0}' """.format(folder)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            self.logger.info(
                "Deleted table from db no longer exists as directory")
        except Error as e:
            self.logger.error("Cant delete table from db: " + str(e))

    def get_tables(self):
        """ Get all tables from db"""

        sql = """SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"""

        try:
            c = self.connection.cursor()
            c.execute(sql, )
            rows = c.fetchall()
            rows = [row[0] for row in rows]
            self.logger.info("Get all folders from db ")
            return rows

        except Error as e:
            self.logger.error("Cant get folders from db: " + str(e))
