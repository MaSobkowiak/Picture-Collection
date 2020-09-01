import pyodbc
import logging
from ._config import get_config
from pathlib import Path


class MSSQL:
    """Class for mssql"""

    def __init__(self, logger):
        self.server = str(get_config("mssql")["host"]+',' + str(get_config("mssql")["port"]))
        self.database = 'Pictures'
        self.username = get_config("mssql")["user"]
        self.password = get_config("mssql")["password"]

        self.logger = logger
        self.connection = self.create_connection()

    def create_connection(self):
        """
        Create a database connection to a MSSQL database
        """

        sql_database = """
            IF  NOT EXISTS (SELECT * FROM sys.databases WHERE name = N'{0}')
                BEGIN
                    CREATE DATABASE [{0}]
                END;
            """.format(self.database)

        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE=master;UID='+self.username+';PWD=' + self.password, autocommit=True)
            cursor = conn.cursor()
            cursor.execute(sql_database)
            cursor.commit()
            conn.commit()

            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE=' +
                                  self.database+';UID='+self.username+';PWD=' + self.password, autocommit=True)

            self.logger.info("Connected to mssql")
            return conn

        except pyodbc.Error as e:
            self.logger.error("Cant connect to mssql: " + str(e))

    def create_table(self, folder: str):
        """ check if database exists, then create table """

        sql_table = """IF NOT EXISTS (SELECT * FROM sysobjects WHERE xtype='U' and name = '{0}')
                CREATE TABLE [{0}] (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    name varchar(255) NOT NULL,
                    path_src varchar(255) NOT NULL,
                    path_tum varchar(255) NOT NULL,
                    path_col varchar(255) NOT NULL,
                    width_src varchar(255) NOT NULL,
                    height_src varchar(255) NOT NULL,
                    width_tum varchar(255) NOT NULL,
                    height_tum varchar(255) NOT NULL,
                    year int NOT NULL,
                    month int NOT NULL,
                    day int NOT NULL,
                    color float,
                    coordinates float,
                    country varchar(255),
                    city varchar(255),
                    label varchar(255)
                )""".format(folder)
        try:
            c = self.connection.cursor()
            c.execute(sql_table)
            c.commit()
            self.connection.commit()

            self.logger.info("Table in mssql checked.")
        except pyodbc.Error as e:
            self.logger.error("Can't create table in mssql: " + str(e))

    def get_names(self, folder):

        sql = """SELECT name FROM [{0}]""".format(folder)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            rows = c.fetchall()

            self.logger.info("Recived names from mssql for " + str(folder) + " folder.")

            return [row[0] for row in rows]

        except pyodbc.Error as e:
            self.logger.error("Cant get names from mssql for " +
                              str(folder) + " folder from db: " + str(e))

    def check_if_photo_exists(self, name, folder):

        sql = """SELECT * FROM [{0}] WHERE name='{1}' """.format(folder, name)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            rows = c.fetchall()
            if rows:
                return True
            else:
                return False

        except pyodbc.Error as e:
            self.logger.error("Error checking mssql: " + str(e))

    def add_photo(self, name, path_src, path_tum, path_col, width_src, height_src, width_tum, height_tum, year, month, day, color, coordinates, country, city, label, folder):
        """ Create new photo entry. Params: Photo object, folder name that foto is in"""

        photo_text = (name, path_src, path_tum, path_col, width_src, height_src, width_tum,
                      height_tum, year, month, day, color, coordinates, country, city, label)

        sql = """ INSERT INTO [{0}] (name, path_src, path_tum, path_col,
                                     width_src, height_src, width_tum, height_tum,
                                      year, month, day,
                                      color, coordinates, country, city, label)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """.format(folder)

        try:
            if not self.check_if_photo_exists(name, folder):
                c = self.connection.cursor()
                c.execute(sql, photo_text)
                c.commit()
                self.connection.commit()

                self.logger.info("Added photo to mssql: " + str(name))
            else:
                self.logger.info("Photo exists in msssql: " + str(name))
        except pyodbc.Error as e:
            self.logger.error("Cant add photo to mssql: " + str(e))

    def delete_photo(self, name, folder):
        """ Delete photo from db by name"""

        sql = """ DELETE FROM [{0}] WHERE name = '{1}' """.format(folder, name)

        try:
            if self.check_if_photo_exists(name, folder):
                c = self.connection.cursor()
                c.execute(sql)
                c.commit()
                self.connection.commit()

                self.logger.info(
                    "Deleted photo from mssql, no longer exists as file")
            else:
                self.logger.info("Can't delete photo, don't exists in mssql")
        except pyodbc.Error as e:
            self.logger.error("Cant delete photo from mssql: " + str(e))

    def delete_table(self, folder):
        """ Delete table from db """

        sql = """DROP TABLE [{0}] """.format(folder)

        try:
            c = self.connection.cursor()
            c.execute(sql)
            c.commit()
            self.connection()

            self.logger.info(
                "Deleted table from mssql no longer exists as directory")
        except pyodbc.Error as e:
            self.logger.error("Cant delete table from mssql: " + str(e))

    def get_tables(self):
        """ Get all tables from db"""

        sql = """
            SELECT TABLE_NAME 
            FROM Pictures.INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            """

        try:
            c = self.connection.cursor()
            c.execute(sql, )
            rows = c.fetchall()
            rows = [row[0] for row in rows]
            self.logger.info("Get all folders from mssql ")
            return rows

        except pyodbc.Error as e:
            self.logger.error("Cant get folders from mssql: " + str(e))
