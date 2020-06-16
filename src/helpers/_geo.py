import socket
import requests
import json
import logging
from ._config import get_config


def _get_country_name(code):

    def _get_name_PL(code):
        obj = json.load(open('src/helpers/countries.json', encoding='utf-8'))
        return obj[code]['PL']

    def _get_name_EN(code):
        obj = json.load(open('src/helpers/countries.json', encoding='utf-8'))
        return obj[code]['EN']

    if get_config("language") == 'PL':
        return _get_name_PL(code)

    elif get_config("language") == 'EN':
        return _get_name_EN(code)

    else:
        return _get_name_PL(code)


def _check_internet_connection():

    logger = logging.getLogger("Geo")

    ip = socket.gethostbyname(socket.gethostname())

    if ip == "127.0.0.1":
        logger.error("No internet connection.")
        return False
    else:
        return True


def _get_location(coordinates: str):
    logger = logging.getLogger("Geo")

    url = 'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json'
    params = {
        'apiKey': 'rMZN1V_Xk_h9O6_1JYELKn4ZJ9aem4daUSrCzburYWw',
        'prox': coordinates,
        'mode': 'retrieveAddresses',
        'maxresults': '1',
        'gen': '9',
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    except (requests.exceptions.HTTPError, requests.exceptions.SSLError)as e:
        logger.error(str(e))
        return None


def get_geotags(coordinates: list, logger):
    """
    Get geotags from "HERE", return None if failed.
        :return country, city, label:
    """

    if coordinates:
        coordinates = str(coordinates[0]) + "," + str(coordinates[1])

        if _check_internet_connection():
            geotags = _get_location(coordinates)

            if geotags is not None and len(geotags['Response']['View']) != 0:

                country = _get_country_name(
                    geotags['Response']['View'][0]['Result'][0]['Location']['Address']['Country'])
                city = geotags['Response']['View'][0]['Result'][0]['Location']['Address']['City']
                label = geotags['Response']['View'][0]['Result'][0]['Location']['Address']['Label']

                logger.info("Recieved all location info.")

                return country, city, label

    return None, None, None
