import pprint
import requests
# import request
import json
import datetime
from decimal import Decimal
from functools import partial
from urllib.parse import urljoin
from collections import namedtuple

from IPython.utils.text import date_format

API_HOST = "https://api.skypicker.com/flights"
Flight = namedtuple("Flight", ["fly_from", "fly_to", "dep_time", "arr_time", "flight_no"])

def make_request(fly_from, fly_to, dep_date, return_date=None):
    """
    Make request function to the KIWI API
    """
    date_from = reformat_date(dep_date)

    if date_from is None:
        print("Incorrect date format! Use YYYY-MM-DD!")
        return None
    return_date = reformat_date(return_date)
    params = {
        "fly_from": fly_from,
        "fly_to": fly_to,
        "date_from": date_from,
        "date_to": date_from,
        "return_from": return_date,
        "return_to": return_date,
        # "adults": 1,
        "partner": "picky",
        "partner_market": "de",
    }

    return partial(requests.get, API_HOST, params)

def reformat_date(date):
    """
    Reformat date from "YYYY-MM-DD" to "DD/MM/YYYY"

    :param date: date in the format  "YYYY-MM-DD"
    :return: date in the format "DD/MM/YYYY" or None if errors have occurred
    """
    try:
        datetime_date = datetime.datetime.strptime(str(date), '%Y-%m-%d')
    except ValueError:
        # print("Incorrect date format")
        return None

    return datetime_date.strftime("%d/%m/%Y") if datetime_date else None

def send_request(request_method):
    response = request_method()
    if response.status_code == 200:
        return response
    else:
        print(f"Something wrong with kiwi: "
              f"Status code:{response.status_code}\n"
              f"{response.text} ")


def fill_route(itinerary):
    flights = []
    for route in itinerary.get("route"):
        flights.append(
            Flight(
                route.get("flyFrom"),
                route.get("flyTo"),
                datetime.datetime.fromtimestamp(route.get("dTime")).strftime("%Y-%m-%d %H:%M:%S"),
                datetime.datetime.fromtimestamp(route.get("aTime")).strftime("%Y-%m-%d %H:%M:%S"),
                route.get("airline") + str(route.get("flight_no")),
            )
        )
    return flights


def find_the_cheapest_itinerary(full_response):
    all_itineraries = full_response.get("data")
    if all_itineraries == []:
        print("Check your dates! No itineraries have found ! (kiwi)")
        return
    return min(all_itineraries, key=lambda x: x.get("price"))


def get_min_price(itinerary):
    return Decimal(itinerary.get("price"))


def sort_itineraries_by_dep_time(full_response: dict):
    # Sort all itineraries by departure time
    all_itineraries = full_response.get("data")
    sorted_itineries =  sorted(all_itineraries, key=lambda x: x.get("route")[0].get("dTime"))[:10]

    # Saving sorted itineraries
    with open("out_files/sorted_itineraries_kiwi.json", "w") as f:
        json.dump(sorted_itineries, f, indent=4)

    print("Sorted itineraries has been saved into 'sorted_itineraries_kiwi.json'\n\n"
          "Departure times (kiwi):")
    [print(i, datetime.datetime.fromtimestamp(route.get("route")[0].get('dTime'))) for i, route in enumerate(sorted_itineries)]
    print("\n")

    return sorted_itineries


if __name__ == '__main__':
    with open("kiwi_response.json", "r") as f:
        data = json.load(f)


    sort_itineraries_by_dep_time(data)