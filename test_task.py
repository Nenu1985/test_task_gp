import requests
import json
from lxml import etree
from decimal import Decimal
import kiwi, dohop
import argparse


class Flights:
    API_HOSTS = {
        "kiwi": "https://api.skypicker.com/flights",
        "dohop": "https://partners-api.dohop.com/api/v3/ticketing/gatwick-connect/DE/EUR",
    }
    DOHOP_TOKEN = {"ticketing-partner": "36fd0d405f4541b7be72d117b574a70f", }

    def __init__(self, fly_from, fly_to, departure_date, return_date=None):
        """
        Create requests methods for APIs, initializing.

        :param fly_from: The IATA code of the departure airport/city. Example KEF (Reykjavik)
        :param fly_to: The IATA code of the arrival airport/city. Example NCE (Nice)
        :param departure_date: The departure date, in the format YYYY-MM-DD
        :param return_date: The optional return date, in the format YYYY-MM-DD
        """
        self.min_price = float("inf")
        self.route = []
        self.response_kiwi = ""
        self.response_dohop = ""
        self.cheapest_kiwi_itinerary = {}
        self.cheapest_dohop_itinerary = {}
        self.cheapest_itinerary = {}
        self.dohop_min_price = float("inf")
        self.kiwi_min_price = float("inf")

        self.request_kiwi = kiwi.make_request(fly_from, fly_to, departure_date, return_date)
        self.request_dohop = dohop.make_request(fly_from, fly_to, departure_date, return_date)



    # python your_script.py KEF NCE 2019-08-13
    def find_cheapest_flight(self, ):
        """
        The main method that do all requirement tasks:
         - makes and saves responses to APIs ;
         - finds the cheapest itinerary;
         - sorts itineraries by departure date;
         - out the necessary data;
        :return: None
        """
        if self.request_kiwi is None or self.request_dohop is None:
            return
        self.response_kiwi = kiwi.send_request(self.request_kiwi)
        self.cheapest_kiwi_itinerary = kiwi.find_the_cheapest_itinerary(self.response_kiwi.json())
        if self.cheapest_kiwi_itinerary is not None:
            self.kiwi_min_price = kiwi.get_min_price(self.cheapest_kiwi_itinerary)

        self.response_dohop = dohop.send(self.request_dohop)
        if self.response_dohop is not None:
            self.cheapest_dohop_itinerary = dohop.find_the_cheapest_itinerary(self.response_dohop.json())
            if self.cheapest_dohop_itinerary is not None:
                self.dohop_min_price = dohop.get_min_price(self.cheapest_dohop_itinerary)

        self.cheapest_itinerary = self.cheapest_kiwi_itinerary \
            if self.kiwi_min_price < self.dohop_min_price \
            else self.cheapest_dohop_itinerary

        self.min_price = min(self.dohop_min_price, self.kiwi_min_price)
        self.filling_route_tuple()
        self.out_requiered_data_task1()

        self.sort_itineraries()

    @staticmethod
    def convert_euro_to_byn(euro_price):
        rates = requests.get("http://www.nbrb.by/Services/XmlExRates.aspx?mode=2")
        daily_rates = etree.XML(rates.content)
        # tree = etree.ElementTree(daily_rates)
        #
        # with open("currency_ex_rates.xml", 'w') as f:
        #     tree.write(f)
        eur_to_byn_rate = Decimal(daily_rates.xpath(".//Currency/CharCode[text()='EUR']/../Rate")[0].text)

        return euro_price * eur_to_byn_rate

    def filling_route_tuple(self):
        """
        Append flights to self.route list
        """
        if self.kiwi_min_price < self.dohop_min_price:
            self.route = kiwi.fill_route(self.cheapest_itinerary)
        else:
            self.route = dohop.fill_route(self.cheapest_itinerary)

    def sort_itineraries(self):
        kiwi.sort_itineraries_by_dep_time(self.response_kiwi.json())
        if self.response_dohop is not None:
            dohop.sort_itineraries_by_dep_time(self.response_dohop.json())

    def out_requiered_data_task1(self):

        with open("out_files/kiwi_response.txt", "w") as f:
            f.write(self.response_kiwi.text)
        print("Kiwi's response has been saved into 'kiwi_response.txt'\n")

        if self.response_dohop is not None:
            with open("out_files/dohop_response.txt", "w") as f:
                f.write(self.response_dohop.text)

            print("Dohop's response has been saved to 'dohop_response.txt'\n")
            print(f"Dohop's' request raw: {self.response_dohop.url}\n")
            print(f"Kiwi's' request raw: {self.response_kiwi.url}\n")

        with open("out_files/cheapest_itinerary.json", "w") as f:
            json.dump(self.cheapest_itinerary, f, indent=4)
        print("Json formatted data with the cheapest itinerary have been saved to 'cheapest_itinerary.json'\n")
        print(f"The cheapest itinerary:".center(40, "~") + "\n"
        f"Found by {'Kiwi API' if self.kiwi_min_price < self.dohop_min_price else 'Dohop API'}\n"
                                                           
        f"Total price = {self.min_price} EUR, {self.convert_euro_to_byn(self.min_price)} BYN\n")
        [print(f"{str(i)}: {flight}") for i, flight in enumerate(self.route)]
        print("\n\n")


if __name__ == '__main__':
    """
    usage: python test_task.py  KEF NCE 2019-11-13
    
    - finds the cheapest flight of different APIs;
    - sorts itineraries;
    - converts the flight price in BYN;
    """
    PARSER = argparse.ArgumentParser(
        description='''
            App finds the cheapest flight between city pairs using\n
        two different flight search APIs:
            1. Dohop ticketing API - api.dohop.com;
            2. Kiwi API - docs.kiwi.com;
            '''
    )

    PARSER.add_argument('fly_from', type=str,
                        help='Number of fotos to download and insert into a collage image',
                        )
    PARSER.add_argument('fly_to', type=str,
                        help='The IATA code of the arrival airport/city. Example NCE (Nice)',
                        )
    PARSER.add_argument('dep_date', type=str,
                        help='The departure date, in the format YYYY-MM-DD (ex: 2019-11-13)',
                        )
    PARSER.add_argument('return_date', type=str, default=None, nargs="?",
                        help='The optional return date, in the format YYYY-MM-DD (ex: 2019-12-12)',
                        )

    ARGS = PARSER.parse_args()

    # Start programm
    f = Flights(ARGS.fly_from, ARGS.fly_to, ARGS.dep_date, ARGS.return_date)
    f.find_cheapest_flight()

