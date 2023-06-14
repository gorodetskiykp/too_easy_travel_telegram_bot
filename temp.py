import requests
import json

url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

payload = {
	"currency": "USD",
	"eapid": 1,
	"locale": "en_US",
	"siteId": 300000001,
	"propertyId": "2108456"
}
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "441f5dd04bmshd43e9490974826ep1e8e90jsn2aa9d85d5de9",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

with open('1.json', 'w') as f:
	f.write(json.dumps(response.json(), indent=4))
