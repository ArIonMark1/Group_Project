from decimal import *
import requests
from http import HTTPStatus
from django.core.exceptions import ValidationError

from createapp.models import Address

GEO_CHECKER_URL = 'https://geocode-maps.yandex.ru/1.x?apikey=fe838c94-89e2-4657-a2ef-061f23ff1a53&format=json'


def check_address(address: str) -> Address:
    geo_response = requests.get(f"{GEO_CHECKER_URL}&geocode={address}")
    if geo_response.status_code != HTTPStatus.OK:
        raise ValidationError('Не удалось соединиться с сервером')
    geo_meta = geo_response.json()
    # Об оценке точности ответа геокодера можно прочитать тут: https://tech.yandex.ru/maps/doc/geocoder/desc/reference/precision-docpage/
    address_components = []
    try:
        geo_object = geo_meta['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        meta = geo_object['metaDataProperty']['GeocoderMetaData']
        precision = meta['precision']
        address_components = meta['Address']['Components']
    except KeyError:
        raise ValidationError('Не удалось проверить корректность адреса')
    if precision == 'exact':
        address = Address()
        address.city = extract_address_comp(address_components, 'locality')
        address.street = extract_address_comp(address_components, 'street')
        address.building = extract_address_comp(address_components, 'house')
        coords = geo_object['Point']['pos'].split()
        address.longitude = Decimal(coords[0])
        address.latitude = Decimal(coords[1])
        return address
    if precision == 'other':
        raise ValidationError('Уточните адрес')
    raise ValidationError('Уточните номер дома')


def extract_address_comp(address_components, kind):
    return next(filter(lambda x: x['kind'] == kind, address_components))['name']
