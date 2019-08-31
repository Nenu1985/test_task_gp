# Test Task for GP Solutions team

The application finds the cheapest flight between city pairs using
two different flight search APIs:
        
1. Dohop ticketing API - api.dohop.com;
2. Kiwi API - docs.kiwi.com;

Features:

    - finds the cheapest flight of different APIs;
    - sorts itineraries;
    - converts the flight price in BYN;
    
##Usage:
```
usage: test_task.py [-h] fly_from fly_to dep_date [return_date]

example:
python test_task.py  KEF NCE 2019-11-13
```
### args:
   - <b>fly_from</b>: The IATA code of the departure airport/city. Example KEF (Reykjavik)
   - <b>fly_to</b>: The IATA code of the arrival airport/city. Example NCE (Nice)
   - <b>departure_date</b>: The departure date, in the format YYYY-MM-DD
   - <b>return_date</b>: The optional return date, in the format YYYY-MM-DD


## OUT
The result of the program is displayed in the console and saved in the "out_files" directory:
- "cheapest_itinerary.json" - json file with the cheapest itinerary;
- "dohop_response.txt" - raw response received by DOHOP API;
- "kiwi_response.txt" - raw response received by KIWI API;
- "sorted_itenerires_dohop.json" - sorted itineraries by departure time received by DOHOP API;
- "sorted_itineraries_kiwi.json" - sorted itineraries by departure time received by KIWI API;

Other information is displayed in the console: price; flights route, etc.

## TEST
There are some tests in the "test.py" file:
```
python3 -m pytest tests.py
```
