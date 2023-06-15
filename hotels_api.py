import requests

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


def search_hotels(city_id, hotels_count, photo_count, begin, end, order):
    endpoint = 'properties/v2/list'
    headers = {
        'X-RapidAPI-Key': X_RapidAPI_Key,
        'X-RapidAPI-Host': X_RapidAPI_Host,
    }
    if order == 'low':
        order = 'PRICE_LOW_TO_HIGH'
    elif order == 'high':
        order = 'PRICE_HIGH_TO_LOW'
    elif order == 'center':
        order = 'DISTANCE'
    else:
        order = ''
    data = {
        "currency": "USD",
        "eapid": 1,
        "resultsSize": int(hotels_count),
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": city_id},
        "checkInDate": {
            "day": begin.day,
            "month": begin.month,
            "year": begin.year,
        },
        "checkOutDate": {
            "day": end.day,
            "month": end.month,
            "year": end.year,
        },
        "rooms": [
            {
                "adults": 2,
                "children": []
            }
        ],
        "sort": order
    }
    response = requests.post(
        url='https://{}/{}'.format(X_RapidAPI_Host, endpoint),
        headers=headers,
        json=data,
    )

    hotels = response.json()
    hotels = hotels['data']['propertySearch']['properties']

    result = []
    for hotel in hotels:
        hotel_id = hotel['id']
        photos, address = get_hotel_details(hotel_id, photo_count)
        result.append(
            {
                'name': hotel['name'],
                'id': hotel_id,
                'price': hotel['price']['options'][0]['formattedDisplayPrice'],
                'address': address,
                'center_dest': '{} {}'.format(
                    hotel['destinationInfo']['distanceFromDestination']['value'],
                    hotel['destinationInfo']['distanceFromDestination']['unit'],
                ),
                'photos': photos,
            }
        )
    return result


def get_hotel_details(hotel_id, photo_count):
    endpoint = 'properties/v2/detail'
    headers = {
        'X-RapidAPI-Key': X_RapidAPI_Key,
        'X-RapidAPI-Host': X_RapidAPI_Host,
    }
    data = {
        "propertyId": str(hotel_id),
    }
    response = requests.post(
        url='https://{}/{}'.format(X_RapidAPI_Host, endpoint),
        headers=headers,
        json=data,
    )
    details = response.json()
    photos = details['data']['propertyInfo']['propertyGallery']['images']
    address = details['data']['propertyInfo']['summary']['location']['address']['addressLine']
    return [photo['image']['url'] for photo in photos][:int(photo_count)], address


if __name__ == '__main__':
    print(get_hotel_details('89021335', 2))
