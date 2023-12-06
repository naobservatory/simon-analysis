#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
import csv
from collections import defaultdict

from datetime import datetime, date

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


def get_duplicated_cities():
    world_city_df = pd.read_csv("worldcities.csv")

    duplicated_cities = []
    us_duplicated_cities = []
    city_counts = world_city_df["city_ascii"].value_counts()
    duplicated_cities = city_counts[city_counts > 1].index.tolist()

    us_entries = world_city_df[world_city_df["country"] == "United States"]
    city_admin_counts = us_entries.groupby(["city_ascii", "admin_name"]).size()
    us_duplicated_cities = city_admin_counts[
        city_admin_counts > 1
    ].index.tolist()

    return duplicated_cities, us_duplicated_cities


def get_flight_duration():
    duplicated_cities, us_duplicated_cities = get_duplicated_cities()
    city_info = defaultdict(tuple)
    us_city_info = defaultdict(tuple)
    us_cities = set()
    with open("worldcities.csv", mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            city_info[row["city_ascii"]] = (row["admin_name"], row["country"])
            if row["country"] == "United States":
                us_cities.add(row["city_ascii"])
                us_city_info[row["city_ascii"]] = (
                    row["admin_name"],
                    row["country"],
                )

    print(us_city_info)
    month_range = range(4, 13)
    day_range = range(1, 32)

    headers = [
        "Origin",
        "Date",
        "Terminal",
        "Equipment",
        "Flight",
        "Airline",
        "State",
        "Nation",
        "Flight Time",
    ]

    dropped_cities = defaultdict(int)

    total_origin_counts = defaultdict(int)

    with open("all_flights.tsv", "w", newline="") as outf:
        writer = csv.writer(outf, delimiter="\t", lineterminator="\n")
        writer.writerow(headers)
        for month in month_range:
            for day in day_range:
                if month in [4, 6, 9, 11] and day == 31:
                    continue
                if date(2023, month, day) < date(2023, 4, 17):
                    continue
                    # first entry is from 2023-04-17
                today = date.today()
                if today < date(2023, month, day):
                    break

                try:
                    flight_data_path = get_arrivals(day, month)
                except:
                    continue

                with open(flight_data_path, newline="") as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)
                    origin_index = headers.index("Origin")
                    departure_time_index = headers.index(
                        "Departure Time"
                    )  # HH:MM
                    arrival_time_index = headers.index("Arrival Time")  # HH:MM
                    departure_date_index = headers.index(
                        "Departure Date"
                    )  # YYYY-MM-DD
                    arrival_date_index = headers.index(
                        "Arrival Date"
                    )  # YYYY-MM-DD
                    terminal_index = headers.index("Terminal")
                    equipment_index = headers.index("Equipment")
                    flight_index = headers.index("Flight")
                    airline_index = headers.index("Airline")

                    for row in reader:
                        origin = row[origin_index]
                        dep_time_str = row[departure_time_index]
                        arr_time_str = row[arrival_time_index]
                        dep_date_str = row[departure_date_index]
                        arr_date_str = row[arrival_date_index]
                        terminal = row[terminal_index]
                        equipment = row[equipment_index]
                        flight = row[flight_index]
                        airline = row[airline_index]

                        if not arr_time_str:
                            print("Flight en route or cancelled")
                            print(row)
                            continue
                        departure_datetime = datetime.strptime(
                            f"{dep_date_str} {dep_time_str}", "%Y-%m-%d %H:%M"
                        )
                        arrival_datetime = datetime.strptime(
                            f"{arr_date_str} {arr_time_str}", "%Y-%m-%d %H:%M"
                        )

                        flight_time = arrival_datetime - departure_datetime
                        if origin in city_info:
                            if (
                                origin in duplicated_cities
                                and origin not in us_cities
                            ):
                                print(
                                    f"{origin}] appears twice in world_cities and is not in the US. Dropping entry"
                                )
                                print(row)
                                dropped_cities[origin] += 1
                                continue
                            elif (
                                origin in duplicated_cities
                                and origin in us_cities
                                and origin in us_duplicated_cities
                            ):
                                print(
                                    f"{origin}City exists twice in the US. Location not resolvable, dropping entry"
                                )
                                print(row)
                                dropped_cities[origin] += 1
                                continue
                            elif (
                                origin in duplicated_cities
                                and origin in us_cities
                                and not origin in us_duplicated_cities
                            ):
                                state, nation = us_city_info[origin]

                            else:
                                state, nation = city_info[origin]

                            writer.writerow(
                                [
                                    origin,
                                    arr_date_str,
                                    terminal,
                                    equipment,
                                    flight,
                                    airline,
                                    state,
                                    nation,
                                    flight_time,
                                ]
                            )
                        else:
                            try:
                                nation = "United States"
                                state = cities_not_in_worldcities[origin]
                                writer.writerow(
                                    [
                                        origin,
                                        arr_date_str,
                                        terminal,
                                        equipment,
                                        flight,
                                        airline,
                                        state,
                                        nation,
                                        flight_time,
                                    ]
                                )
                            except KeyError:
                                print(
                                    f"{origin} not in worldcities or cities_not_in_worldcities"
                                )
                                print(row)
                                dropped_cities[origin] += 1
                                continue
    print(dropped_cities)


def start():
    get_flight_duration()


if __name__ == "__main__":
    start()
