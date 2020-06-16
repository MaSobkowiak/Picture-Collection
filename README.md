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
    "photos": "string",        -> root directory of our photos.
    "thumbnail": "string",     -> name of subfolder for thumbnails, if not in config, thumbnails are not created.
    "color": "string",         -> name of subfolder for colors, if not in config, colors are not created.
    "backups": [               -> list of directories for backup
      "string",
      "string"
    ]
  },
  "geo": {                       -> HERE app id and app code
    "APP_ID": "string",
    "APP_CODE": "string"
  },
  "thumbnail_size": "int"    -> thumbnail expected size (smaller side od photo)
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
