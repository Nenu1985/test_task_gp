"""
Test module
 python3 -m pytest tests.py
"""
import json
from lxml import etree
from decimal import Decimal
import test_task, kiwi, dohop

# Reykjavik (airport code KEF) to Nice (airport code NCE), departing on 13.8.2019 and returning 18.8.2019,
# Reykjavik to Stockholm (airport codes ARN, BMA, NYO), departing on 6.8.2019 and returning 15.8.2019
# Minsk (MSQ) to Pskov(PKV), departure on 13.8.2019 and returning 18.8.2019

params = [

    {
        "fly_from": "KEF",  # 0 one side
        "fly_to": "NCE",
        "dep_date": "2019-11-13",
    },
    {
        "fly_from": "KEF",  # 1 round trip
        "fly_to": "NCE",
        "dep_date": "2019-11-13",
        "return_date": "2019-11-18"
    },
    {
        "fly_from": "KEF",  # 2 past trip
        "fly_to": "NCE",
        "dep_date": "2019-08-13",
    },
    {
        "fly_from": "KEF",  # 3 Sweden trip
        "fly_to": "ARN",
        "dep_date": "2019-11-13",
        "return_date": "2019-11-20"
    },
    {
        "fly_from": "MSQ",  # 4 Pskov trip
        "fly_to": "PKV",
        "dep_date": "2019-11-13",
        "return_date": "2019-11-18"
    },
]

json_kiwi_response = {}
with open("test_files/kiwi_response.json", "r") as f:
    json_kiwi_response = json.load(f)

json_dohop_response = {}
with open("test_files/dohop_response.json", "r") as f:
    json_dohop_response = json.load(f)

daily_ex_rates = {}
with open("test_files/currency_ex_rates.xml", "r") as f:
    tree = etree.parse(f)
    daily_ex_rates = tree.getroot()


class TestRequests(object):
    def test_kiwi_request(self):
        request = kiwi.make_request(**params[0])

        assert request.args[0] == 'https://api.skypicker.com/flights'

        assert request.args[1] == {
            'fly_from': 'KEF',
            'fly_to': 'NCE',
            'date_from': '13/11/2019',
            'date_to': '13/11/2019',
            'return_from': None,
            'return_to': None,
            'partner': 'picky',
            'partner_market': 'de'
        }

    def test_kiwi_request_round_trip(self):
        request = kiwi.make_request(**params[1])

        assert request.args[0] == 'https://api.skypicker.com/flights'

        assert request.args[1] == {
            'fly_from': 'KEF',
            'fly_to': 'NCE',
            'date_from': '13/11/2019',
            'date_to': '13/11/2019',
            'return_from': '18/11/2019',
            'return_to': '18/11/2019',
            'partner': 'picky',
            'partner_market': 'de'
        }

    def test_dohop_request(self):
        request = dohop.make_request(**params[0])

        assert request.args[0] == 'https://partners-api.dohop.com/api/v3/ticketing/gatwick-connect/DE/EUR/KEF/NCE/2019-11-13/'
        assert request.keywords["params"] == {'ticketing-partner': '36fd0d405f4541b7be72d117b574a70f'}

    def test_dohop_request_round_trip(self):
        request = dohop.make_request(**params[1])

        assert request.args[0] == 'https://partners-api.dohop.com/api/v3/ticketing/gatwick-connect/DE/EUR/KEF/NCE/2019-11-13/2019-11-18'
        assert request.keywords["params"] == {'ticketing-partner': '36fd0d405f4541b7be72d117b574a70f'}


class TestOffline:
    def test_kiwi_cheapest_itinerary(self):

        assert len(json_kiwi_response.get("data")) == 238

        cheapest_itinerary = kiwi.find_the_cheapest_itinerary(json_kiwi_response)

        assert cheapest_itinerary.get("price") == 62
        assert kiwi.get_min_price(cheapest_itinerary) == 62


    def test_dohop_cheapest_itinerary(self):

        assert len(json_dohop_response.get("itineraries")) == 6

        cheapest_itinerary = dohop.find_the_cheapest_itinerary(json_dohop_response)

        assert dohop.get_min_price(cheapest_itinerary) == Decimal('275.28769712448121254055877216160297393798828125')

    def test_currency_exange_rate(self):

        rate = Decimal(daily_ex_rates.xpath(".//Currency/CharCode[text()='EUR']/../Rate")[0].text)
        assert rate == Decimal('2.3175')

class TestOnline:
    def test_kiwi_response(self):
        request = kiwi.make_request(**params[0])
        response = kiwi.send_request(request)

        assert response.status_code == 200
        data = response.json()
        assert len(data.get("data")) > 0, "Check your dates!"

    def test_dohop_response(self):
        request = dohop.make_request(**params[0])
        response = dohop.send(request)
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("itineraries")) > 0, "Check your dates!"

    def test_kiwi_response_past_trip(self):
        request = kiwi.make_request(**params[2])
        response = kiwi.send_request(request)

        assert response.status_code == 200
        data = response.json()
        assert len(data.get("data")) == 0, "Check your dates!"

    def test_dohop_response_past_trip(self):
        request = dohop.make_request(**params[2])
        response = dohop.send(request)
        assert response is None

    def test_currency_exchange(self):
        # Change 100 EUR in BYN:
        byn_count = test_task.Flights.convert_euro_to_byn(100)
        assert 220 < byn_count < 240