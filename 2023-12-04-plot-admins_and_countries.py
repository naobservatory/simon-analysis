#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from math import sqrt

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


def plot_flight_origins():
    cities_data = pd.read_csv("worldcities.csv")
    city_info = {
        row["city_ascii"]: (row["admin_name"], row["country"])
        for index, row in cities_data.iterrows()
    }
    month_range = range(5, 13)
    day_range = range(1, 32)

    headers = [
        "Origin",
        "Terminal",
        "Equipment",
        "Flight",
        "Airline",
        "State",
        "Nation",
    ]

    cities_not_in_worldcities = set()
    with open("flight_data/all_flights.csv", "w") as outf:
        writer = csv.writer(outf)
        writer.writerow(headers)
        for month in month_range:
            for day in day_range:
                try:
                    flight_data_path = get_arrivals(day, month)
                except subprocess.CalledProcessError:
                    print(f"no data for {month}/{day}")
                    continue
                with open(flight_data_path, newline="") as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)
                    origin_index = headers.index("Origin")
                    terminal_index = headers.index("Terminal")
                    equipment_index = headers.index("Equipment")
                    flight_index = headers.index("Flight")
                    airline_index = headers.index("Airline")

                    for row in reader:
                        origin = row[origin_index]
                        terminal = row[terminal_index]
                        equipment = row[equipment_index]
                        flight = row[flight_index]
                        airline = row[airline_index]

                if origin in city_info:
                    state, nation = city_info[origin]
                else:
                    cities_not_in_worldcities.add(origin)
                    state = "origin not in worldcities"
                    nation = "origin not in worldcities"
                writer.writerow(
                    [
                        origin,
                        terminal,
                        equipment,
                        flight,
                        airline,
                        state,
                        nation,
                    ]
                )
    print(cities_not_in_worldcities)


def start():
    plot_flight_origins()


if __name__ == "__main__":
    start()
