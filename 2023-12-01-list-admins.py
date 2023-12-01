#!/usr/bin/env python3

import pandas as pd
import subprocess
import os
from collections import defaultdict

cities_not_in_worldcities = {
    "Provincetown": "Massachusetts",
    "Bar Harbor": "Maine",
    "Raleigh/Durham": "North Carolina",
    "Martha's Vineyard": "Massachusetts",
    "Bedford/Hanscom": "Massachusetts",
    "Saranac Lake": "New York",
    "Dulles": "Virginia",
    "Westchester County": "New York",
    "Hyannis": "Massachusetts",
    "Saint Louis": "Missouri",
    "Farmingdale": "New York",
    "Belmar": "New Jersey",
    "Pellston": "Michigan",
    "Greensboro/High Point": "North Carolina",
    "Latrobe": "Pennsylvania",
    "Teterboro": "New Jersey",
    "Stowe": "Vermont",
    "Westhampton Beach": "New York",
    "Page": "Arizona",
    "Selinsgrove": "Pennsylvania",
    "Hilton Head": "South Carolina",
    "Eastport": "Maine",
    "Salisbury-Ocean City": "Maryland",
    "Dillon": "Montana",
    "Placida": "Florida",
    "Laporte": "Indiana",
    "Saint Paul": "Minnesota",
    "Farmville": "Virginia",
    "Saint Augustine": "Florida",
    "Mt Vernon": "Illinois",
    "Fishers Island": "New York",
    "Aspen": "Colorado",
    "Ocean Reef": "Florida",
    "Montauk Point": "New York",
    "Wiscasset": "Maine",
    "Port Clinton": "Ohio",
    "Manteo": "North Carolina",
    "Islesboro": "Maine",
    "Houlton": "Maine",
    "Currituck": "North Carolina",
    "Lake Placid": "New York",
    "Block Island": "Rhode Island",
    "Rangeley": "Maine",
    "Reedsville": "Pennsylvania",
    "Kailua-Kona": "Hawaii",
    "Edenton": "North Carolina",
    "Millinocket": "Maine",
    "Winnsboro": "Louisiana",
    "Great Barrington": "Massachusetts",
    "Blue Bell": "Pennsylvania",
    "Kayenta": "Arizona",
    "Bristol, VA/Johnson City/Kingsport": "Virginia",
    "Mount Pocono": "Pennsylvania",
    "Waller County": "Texas",
    "Thomson": "Georgia",
    "Saint Thomas": "Virgin Islands",
    "Lorain/Elyria": "Ohio",
}


def get_arrivals(day, month):
    if not os.path.exists("flight_data"):
        os.makedirs("flight_data")
    flight_data_path = f"flight_data/2023-{month:02d}-{day:02d}.csv"
    if not os.path.exists(flight_data_path):
        subprocess.check_call(
            [
                "aws",
                "s3",
                "cp",
                f"s3://nao-bostraffic/Data/Arrivals/2023-{month:02d}-{day:02d}_BOS_Arrivals.csv",
                flight_data_path,
            ]
        )
    return flight_data_path


def extract_flight_origin_data():
    # https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.76.zip
    cities_data = pd.read_csv("worldcities.csv")
    cities = cities_data["city_ascii"].values

    unknown_counts = defaultdict(int)
    total_origin_counts = defaultdict(int)

    month_range = range(4, 13)
    day_range = range(1, 32)
    for month in month_range:
        for day in day_range:
            try:
                flight_data_path = get_arrivals(day, month)
            except:
                print(f"No data for {month}-{day}")
                continue
            flight_data = pd.read_csv(flight_data_path)

            for origin_city in flight_data["Origin"].values:
                if origin_city not in cities:
                    try:
                        administrative_area = cities_not_in_worldcities[
                            origin_city
                        ]
                        total_origin_counts[administrative_area] += 1
                    except:
                        administrative_area = "Unknown"

                        unknown_counts[origin_city] += 1
                        total_origin_counts[administrative_area] += 1

                else:
                    administrative_area = cities_data[
                        cities_data["city_ascii"] == origin_city
                    ][["admin_name"]].values[0][0]
                    total_origin_counts[administrative_area] += 1

    with open("unassigned_cities.tsv", "w") as f:
        for k, v in unknown_counts.items():
            f.write(f"{k}\t{v}\n")

    with open("total_origin_counts.tsv", "w") as f:
        for k, v in total_origin_counts.items():
            f.write(f"{k}\t{v}\n")


def start():
    extract_flight_origin_data()


if __name__ == "__main__":
    start()
