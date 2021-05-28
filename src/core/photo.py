import re
import logging
from datetime import datetime
from PIL import Image, ImageChops
import cv2
import numpy as np
import time
import os
from sklearn.cluster import KMeans
from collections import Counter
from pathlib import Path
from base64 import b64encode
from ..helpers import get_config, get_geotags, SQLite, MSSQL


class Photo:

    def __init__(self, path):
        """
        1. file name 2. folder name 3. list of phots that were processed, this helps when changing name so they dont repeat
        """
        self.logger = logging.getLogger(
            str(self.__class__.__name__ + ": " + path.name))

        self.name = self.check_name(path)

        self.path_src = Path(str(path.parent) + "/" + self.name)

        self.path_tum = Path(str(path.parent) + "/" +
                             get_config("paths")["thumbnail"] + "/" + self.name)

        self.path_col = Path(str(path.parent) + "/" +
                             get_config("paths")["color"] + "/" + self.name)

        self.year, self.month, self.day, self.hour, self.minute, self.second = self.get_date_from_name()

        self.coordinates = self.get_coordinates()
        self.country, self.city, self.label = get_geotags(
            self.coordinates, self.logger)

        self.width_src, self.height_src = self.get_photo_size()
        self.width_tum, self.height_tum = self.get_thumbnail_size()

        self.create_thumbnail()

        self.color = self.create_color()

        self.base64_src = "" #self.get_base64_string(self.path_src)

        self.base64_tum = self.get_base64_string(self.path_tum)

    def add_to_db(self):
        sqlite = SQLite(self.logger)
        sqlite.add_photo(self.name, str(self.path_src), str(self.path_tum), str(self.path_col), self.width_src, self.height_src, self.width_tum, self.height_tum,
                         self.year, self.month, self.day, self.color, self.format_coordinates(), self.country, self.city, self.label, self.path_src.parent.name, self.base64_src, self.base64_tum)

        if get_config("mssql") is not None:
            mssql = MSSQL(self.logger)
            mssql.add_photo(self.name, str(self.path_src), str(self.path_tum), str(self.path_col), self.width_src, self.height_src, self.width_tum, self.height_tum,
                            self.year, self.month, self.day, self.color, self.format_coordinates(), self.country, self.city, self.label, self.path_src.parent.name)

    def format_coordinates(self):
        if self.coordinates:
            return', '.join(map(str, self.coordinates))
        else: 
            return None

    def check_name(self, path):
        r = re.compile(
            r'([12][0-9]{3}-[0-1][0-9]-[0-3][0-9]_[0-2][0-9]\.[0-6][0-9]\.[0-6][0-9])(_[0-9])*(\.jpg|\.png|\.jpeg|\.JPG|\.JPEG|\.PNG)$')

        if re.match(r, path.name):
            self.logger.info("Name match patern.")
            return path.name

        else:
            files = [f.name for f in path.parent.iterdir() if f.is_file()]
            file_fomat = (
                re.search(r'(\.jpg|\.png|\.jpeg|\.JPG|\.JPEG|\.PNG)', path.name)).group(0)

            file_date = self.get_date_taken(path)
            filename = str(file_date + file_fomat)
            i = 1

            while filename in files:
                
                with Image.open(str(path)) as c_img:
                    with Image.open(Path(path.parent, filename)) as f_img:
                        dif_img = ImageChops.difference(c_img, f_img)

                if dif_img.getbbox() is None:
                    Path(path.parent, filename).unlink()
                    self.logger.info("Deleted copy of photo.")
                    break
                else:
                    filename = str(file_date + "_" + str(i) + file_fomat)
                    i += 1

            self.logger = logging.getLogger(
                str(self.__class__.__name__ + ": " + filename))

            path.rename(str(path.parent) + "/" + filename)

            self.logger.info("Changed name: " +
                             str(path.name) + " -> " + filename)

            return filename

    def get_date_taken(self, path):
        """
        Get timestamp of photo.
        If date taken in metadata its converted to "%Y-%m-%d_%H.%M.%S", else it's set as file modified time.
        """
        exifTime = self.get_metadata(path=path, parameter="date_taken")

        if exifTime is None:
            date_time = datetime.fromtimestamp(path.stat().st_mtime)
        else:
            date_time = datetime.strptime(exifTime, '%Y:%m:%d %H:%M:%S')

        return date_time.strftime("%Y-%m-%d_%H.%M.%S")

    def get_base64_string(self, path):
        """
        Get base64 string from photo
        """
        with open(path, "rb") as image_file:
            base64_bytes = b64encode(image_file.read())

            base64_string = base64_bytes.decode('utf-8')

        self.logger.info("Generated base64 string.")
        return base64_string

    def get_metadata(self, parameter, path=None,):
        """
        Get exif data of file.
        parameter: "date_taken" "orientation" "gps_info"
        """
        date_taken = 36867
        orientation = 274
        gps_info = 34853

        if path is not None:
            img = Image.open(path)
        else:
            img = Image.open(self.path_src)

        exifDataRaw = img._getexif()

        if exifDataRaw is not None:
            if parameter == "date_taken" and date_taken in exifDataRaw:
                return exifDataRaw[date_taken]

            elif parameter == "orientation" and orientation in exifDataRaw:
                return exifDataRaw[orientation]

            elif parameter == "gps_info" and gps_info in exifDataRaw:
                return exifDataRaw[gps_info]

        return None

    def get_date_from_name(self):

        r = re.compile(
            r'([12][0-9]{3})-([0-1][0-9])-([0-3][0-9])_([0-2][0-9])\.([0-6][0-9])\.([0-6][0-9])(_[0-9])*(\.jpg|\.png|\.jpeg|\.JPG|\.JPEG|\.PNG)')

        date = re.search(r, self.name)

        return int(date.group(1)), int(date.group(2)), int(date.group(3)), int(date.group(4)), int(date.group(5)), int(date.group(6))

    def get_coordinates(self):
        """
        Get latitiude, longtitiude and altitiude from exif data of photo
        """
        def get_decimal_from_dms(dms, ref):
            try:
                degrees = dms[0][0] / dms[0][1]
                minutes = dms[1][0] / dms[1][1] / 60.0
                seconds = dms[2][0] / dms[2][1] / 3600.0

                if ref in ['S', 'W']:
                    degrees = -degrees
                    minutes = -minutes
                    seconds = -seconds

                return round(degrees + minutes + seconds, 5)
            except:
                return None

        geotags = self.get_metadata(parameter="gps_info")

        if geotags is not None:
            dimmensions = []
            # latitiude
            dimmensions.append(get_decimal_from_dms(
                geotags.get(2), geotags.get(1)))
            # longtitiude
            dimmensions.append(get_decimal_from_dms(
                geotags.get(4), geotags.get(3)))
            # altitiude
            dimmensions.append(get_decimal_from_dms(
                geotags.get(7), None))

            if None in dimmensions:
                self.logger.error("Cant convert geotags")
                return []
            else:
                self.logger.info("Geotags converted")
                return dimmensions

        else:
            self.logger.warn("No geotags")
            return []

    def get_photo_size(self):
        """
        Return photo size.
            :return tuple (width,height):
        """
        img = Image.open(self.path_src)
        return img.size

    def get_thumbnail_size(self):
        """
        Return smaller size of processed photo with preserved ratio.
            :return tuple (width,height):
        """

        thumbnail_size = int(get_config("thumbnail_size"))

        if self.width_src < self.height_src:
            ratio = self.width_src / thumbnail_size
            width = thumbnail_size
            height = int(self.height_src / ratio)
        else:
            ratio = self.height_src / thumbnail_size
            height = thumbnail_size
            width = int(self.width_src / ratio)

        size = (width, height)
        return size

    def create_thumbnail(self):
        """
        Create thumbnail for photo. Smaller size improve loading time of page.
        """

        if not self.path_tum.exists():
            img = Image.open(self.path_src)

            img = img.resize(
                [self.width_tum, self.height_tum], Image.ANTIALIAS)

            if self.get_metadata("orientation") in (6, 5):
                img = img.rotate(-90, expand=True)

            elif self.get_metadata("orientation") in (7, 8):
                img = img.rotate(90, expand=True)

            img.save(self.path_tum)

            self.logger.info("Thumbnail created")
        else:
            self.logger.info("Thumbnail existed")

    def create_color(self):

        def save_pixel(color):

            color20 = np.full((20, 20, 3), color, dtype='uint8')
            color_bgr = cv2.cvtColor(color20, cv2.COLOR_HSV2BGR)
            cv2.imwrite(str(self.path_col), color_bgr)

        def get_img_color(path, number_of_clusters):
            """
            img is (path_photos + "/" + folder + "/thumbnails/" + picture)
            dominant color is found by running k means on the
            pixels & returning the centroid of the largest cluster
            """
            # TODO determine how many cluster should be used -> probably 2
            def get_dominant_color(hsv_image, number_of_clusters):
                # reshape the image to be a list of pixels
                hsv_image = hsv_image.reshape(
                    (hsv_image.shape[0] * hsv_image.shape[1], 3))
                # cluster and assign labels to the pixels
                clt = KMeans(n_clusters=number_of_clusters)
                labels = clt.fit_predict(hsv_image)
                # count labels to find most popular
                label_counts = Counter(labels)
                # subset out most popular centroid
                dominant_color = clt.cluster_centers_[
                    label_counts.most_common(1)[0][0]]
                return list(dominant_color)

            # read in image of interest
            bgr_image = cv2.imread(str(path))
            # convert to HSV; this is a better representation of how we see color
            hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

            # extract dominant color
            dominant_color = get_dominant_color(hsv_image, number_of_clusters)
            return dominant_color

        if not self.path_col.exists():
            st = time.time()
            if self.path_tum.exists():
                dominant_color = get_img_color(self.path_tum, 3)
            else:
                dominant_color = get_img_color(self.path_src, 3)

            save_pixel(dominant_color)

            self.logger.info("Color created in: " +
                             str(time.time() - st) + " s")

            return dominant_color[0]
        else:
            self.logger.info("Color existed")
            # number of clusters == 1 bcs the color picture has only one color
            return get_img_color(self.path_col, 1)[0]
