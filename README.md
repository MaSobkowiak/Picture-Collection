# Picture collection

Picture collection is a Python programe for dealing and cataloging directories with pictures.
It creates SqlLite database, and fills it up with informations about photos eg. date taken, dominant color, coorinates, country etc. It uses [HERE](https://www.here.com/platform/location-based-services) lociation services for retrieving data about geolocation. It can create mirror of our pictures directory in remote or local destination.

## Functionalities

- Creating SqlLite database with table for every folder in root pictures directory.
- Retrieving metadata from photos eg. date taken, photo orientation, photo coordinates.
- Retrieving dominant color of photo.
- Using [HERE](https://www.here.com/platform/location-based-services) converts geolocation metadata into redable informations eg. City, Country, Label
- Creating thumbnail for every photo.
- Creating backup of root in multiple, remote or local directiories.

## Config

```json
{
  "paths": {
    "photos": "root directory of our photos.",
    "thumbnail": "name of subfolder for thumbnails.",
    "color": "name of subfolder for colors",
    "backups": [
      "directories for backup",
      "directories for backup"
    ]
  },
  "geo": {
    "APP_ID": " HERE app id",
    "APP_CODE": "HERE app code"
  },
  "language": "PL",          -
  "thumbnail_size": "thumbnail expected size (smaller side od photo)"
}

```

## Used packages

- [Pillow](https://pypi.org/project/Pillow/)
- [OpenCV](https://pypi.org/project/opencv-python/)
- [numpy](https://pypi.org/project/numpy/)
- [requests](https://pypi.org/project/requests/)
- [sklearn](https://pypi.org/project/sklearn/)

## Usage

Install importatnt packages

```bash
pip install -r requirements.txt
```

and then run the script

```python
python3 run.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
