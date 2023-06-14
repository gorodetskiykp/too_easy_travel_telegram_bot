import requests
import json

from credential import X_RapidAPI_Host, X_RapidAPI_Key


def search_cities(city):
    endpoint = 'locations/v3/search'
    headers = {
        'X-RapidAPI-Key': X_RapidAPI_Key,
        'X-RapidAPI-Host': X_RapidAPI_Host,
    }
    data = {
        'q': city,
        'locale': 'ru_RU',
        'langid': '1033',
        'siteid': '300000001'
    }
    response = requests.get(
        url='https://{}/{}'.format(X_RapidAPI_Host, endpoint),
        headers=headers,
        params=data,
    )

    locations = response.json()

    result = []
    for location in locations['sr']:
        if location['type'] == 'CITY':
            print(location['regionNames']['fullName'])
            result.append(
                {
                    'id': location['gaiaId'],
                    'name': location['regionNames']['fullName'],
                }
            )

    return result


def search_hotels(city_id, hotels_count, photo_count):
    endpoint = 'properties/v2/list'
    headers = {
        'X-RapidAPI-Key': X_RapidAPI_Key,
        'X-RapidAPI-Host': X_RapidAPI_Host,
    }
    data = {
        "currency": "USD",
        "eapid": 1,
        "resultsSize": int(hotels_count),
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": { "regionId": city_id },
        "checkInDate": {
            "day": 10,
            "month": 6,
            "year": 2023
        },
        "checkOutDate": {
            "day": 20,
            "month": 6,
            "year": 2023
        },
        "rooms": [
            {
                "adults": 2,
                "children": []
            }
        ],
        "sort": "PRICE_LOW_TO_HIGH"
    }
    response = requests.post(
        url='https://{}/{}'.format(X_RapidAPI_Host, endpoint),
        headers=headers,
        json=data,
    )

    with open('1.json', 'w') as f:
        f.write(json.dumps(response.json(), indent=4))

    hotels = response.json()
    hotels = hotels['data']['propertySearch']['properties']



    result = []
    for hotel in hotels:
        result.append(
            {
                'name': hotel['name'],
                'id': hotel['id'],
                'price': hotel['price']['options'][0]['formattedDisplayPrice'],
                'address': 'адрес',
                'center_dest': 'как далеко от центра',
                'photos': [
                    'https://www.momondo.com/himg/08/21/f5/leonardo-2684146-Exterior_O-202639.jpg',
                    'https://cdn.worldota.net/t/1024x768/content/b9/2e/b92e343f087293fe6c5274f508825ae129862864.jpeg',
                ]
            }
        )

    return result



