import requests
import json
import datetime
from decimal import Decimal
from functools import partial
from kiwi import Flight

API_HOST = "https://partners-api.dohop.com/api/v3/ticketing/gatwick-connect/DE/EUR"
DOHOP_TOKEN = {"ticketing-partner": "36fd0d405f4541b7be72d117b574a70f", }

def make_request(fly_from, fly_to, dep_date, return_date=None):
    """
    Make request function to the DOHOP API
    """
    date_from = reformat_date(dep_date)
    if date_from is None:
        print("Incorrect date format! Use YYYY-MM-DD!")
        return None
    return partial(requests.get, "/".join([
            API_HOST,
            fly_from,
            fly_to,
            date_from,
            reformat_date(return_date) if return_date else "",
        ]), params=DOHOP_TOKEN)

def reformat_date(date):
    """
    Checking the format to accord with the format YYYY-MM-DD
    """
    try:
        datetime_date = datetime.datetime.strptime(str(date), '%Y-%m-%d')
    except ValueError:
        return None
    return datetime_date.strftime("%Y-%m-%d") if datetime_date else None

def send(request_method):
    response = request_method()
    if response.status_code == 200:
        return response
    else:
        print(f"Something wrong with dohop: "
              f"Status code:{response.status_code}\n"
              f"{response.text} ")


def fill_route(itinerary):
    flights = []
    for route in itinerary.get("flights-out") + itinerary.get("flights-home"):
        flights.append(
            Flight(
                route[0][0][0],  # fly_from
                route[0][0][1],  # fly_to
                route[0][0][3],  # dep_date
                route[0][0][4],  # arr_date
                route[0][0][2],  # flight_no
            )
        )
    return flights


def find_the_cheapest_itinerary(full_response):
    all_itineraries = full_response.get("itineraries")

    if all_itineraries == []:
        print("Check your dates! No itineraries have found ! (dohop)")
        return

    return min(all_itineraries, key=lambda x: x.get("fare-combinations")[0]
               .get("fare-including-fee")
               .get("amount"))


def get_min_price(itinerary):
    return Decimal(itinerary.get("fare-combinations")[0]
                   .get("fare-including-fee")
                   .get("amount"))


def sort_itineraries_by_dep_time(full_response: dict):
    # Sort all itineraries by departure time
    all_itineraries = full_response.get("itineraries")
    sorted_itineries = sorted(all_itineraries, key=lambda x: datetime.datetime.strptime(x.get("flights-out")[0][0][3], '%Y-%m-%d %H:%M'))[:10]
    # Saving sorted itineraries
    with open("out_files/sorted_itineraries_dohop.json", "w") as f:
        json.dump(sorted_itineries, f, indent=4)

    print("Sorted itineraries has been saved into 'sorted_itineraries_dohop.json'\n\n"
          "Departure times (dohop):")
    [print(i, route.get("flights-out")[0][0][3]) for i, route in enumerate(sorted_itineries)]
    return sorted_itineries


if __name__ == '__main__':
    with open("dohop_response.json", "r") as f:
        data = json.load(f)

    sort_itineraries_by_dep_time(data)
