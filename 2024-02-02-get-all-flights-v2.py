#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime, date
from zoneinfo import ZoneInfo
import re

airports_not_in_sheet = {  # Fix missing airport codes
    "MCO": "FL",
    "BHB": "ME",
    "PVC": "MA",
    "TEB": "NJ",
    "RUT": "VT",
    "MSS": "NY",
    "SLK": "NY",
    "STI": "Dominican Republic",
    "BED": "MA",
    "PSM": "NH",
    "FOK": "NY",
    "FRG": "NY",
    "MMU": "NJ",
    "PWK": "IL",
    "BLM": "NJ",
    "PLS": "Turks and Caicos Islands",
    "LCI": "NH",
    "BVY": "MA",
    "OPF": "FL",
    "OXC": "CT",
    "OWD": "MA",
    "BCT": "FL",
    "VNY": "CA",
    "CGF": "OH",
    "PDK": "GA",
    "KJZI": "SC",
    "PTK": "MI",
    "KOQU": "RI",
    "PSF": "MA",
    "ILG": "DE",
    "5B2": "NY",
    "NHZ": "ME",
    "APA": "CO",
    "AGC": "PA",
    "LUK": "OH",
    "CTH": "PA",
    "PNE": "PA",
    "MVL": "VT",
    "MTN": "MD",
    "CDW": "NJ",
    "ESN": "MD",
    "EWB": "MA",
    "SUA": "FL",
    "JPX": "NY",
}


def get_time_zones():
    time_zone_dict = {}
    with open("time_zones.csv", mode="r", encoding="utf-8") as file:
        for line in file:
            location, time_zone = line.split(",")
            time_zone_dict[location] = time_zone.strip()
    return time_zone_dict


def time_to_float(t):
    return t.hour + t.minute / 60 + t.second / 3600


def get_arrivals(day, month, year):
    if not os.path.exists("flight_data"):
        os.makedirs("flight_data")
    flight_data_path = f"flight_data/{year}-{month:02d}-{day:02d}.csv"
    if not os.path.exists(flight_data_path):
        subprocess.check_call(
            [
                "aws",
                "s3",
                "cp",
                f"s3://nao-bostraffic/Data/Arrivals/{year}-{month:02d}-{day:02d}_BOS_Arrivals.csv",
                flight_data_path,
            ]
        )
    return flight_data_path


def get_state_code_dict():
    state_code_dict = {}
    with open("state_code_to_name.tsv", mode="r", encoding="utf-8") as file:
        # source: https://docs.google.com/spreadsheets/d/1wU-Ibw9lOplcBMbCbfhgz3GeDx10yZ7iCQY1uHcMu88/edit#gid=0
        # skip first line which contains source
        next(file)
        csv_reader = csv.DictReader(file, delimiter="\t")
        for row in csv_reader:
            state_code_dict[row["state_code"]] = row["state_name"]
    return state_code_dict


def get_airport_codes():
    non_us_codes = defaultdict(tuple)
    us_codes = defaultdict(tuple)
    with open(
        # source: https://docs.google.com/spreadsheets/u/1/d/1eepIWOHicQsLyZsb0mSXGPTXDp3vlql-aGuy1AWJED0/htmlview#
        # TODO: Use official IATA data, this sheet has a couple of mistakes
        # that I have to account for below
        "Airport Codes by Country - Airport Codes List .tsv",
        mode="r",
        encoding="utf-8",
    ) as file:
        csv_reader = csv.DictReader(file, delimiter="\t")
        for row in csv_reader:
            fine_location, location, airport_code = (
                row["City"],
                row["Country "],  # note the space at the end of the key
                row["Code"],
            )
            if location == "USA":
                try:
                    if airport_code == "DCA":
                        city = "Washington"
                        state = "DC"
                    elif airport_code == "SFO":
                        city = "San Francisco"
                        state = "CA"
                    elif airport_code == "IAD":
                        city = "Washington"
                        state = "VA"
                    elif airport_code == "BWI":
                        city = "Baltimore"
                        state = "MD"
                    elif airport_code == "ATL":
                        city = "Atlanta"
                        state = "GA"
                    elif airport_code == "BUF":
                        city = "Buffalo"
                        state = "NY"
                    elif airport_code == "SJU":
                        city = "San Juan"
                        state = "PR"
                    elif airport_code == "IAG":
                        city = "Niagara Falls"
                        state = "NY"
                    elif airport_code == "TRI":
                        city = "Blountville"
                        state = "TN"
                    else:
                        bits = fine_location.split(", ")
                        city = bits[0]
                        state = bits[-1]
                        state = state.split(" ")[0]
                except:
                    continue
                us_codes[airport_code] = state
                continue
            else:
                if airport_code == "SJU":
                    city = "San Juan"
                    state = "PR"
                    us_codes[airport_code] = state
                    continue
                if "," in location:
                    country = location.split(", ")[1]
                else:
                    country = location
                non_us_codes[airport_code] = country

    return us_codes, non_us_codes


def create_all_flights_tsv():
    us_codes, non_us_codes = get_airport_codes()
    state_code_dict = get_state_code_dict()
    time_zone_dict = get_time_zones()

    month_range = range(1, 13)
    day_range = range(1, 32)
    years = [2023, 2024]
    headers = [
        "Origin",
        "Origin Code",
        "Date",
        "Terminal",
        "Equipment",
        "Flight",
        "Airline",
        "Nation",
        "State",
        "Flight Time",
    ]
    missing_airport_codes = defaultdict(int)
    total_origin_counts = defaultdict(int)
    total_hour_counts = defaultdict(int)
    flight_times = defaultdict(int)
    plot_flight_times = defaultdict(int)
    flight_exclusions = defaultdict(int)
    included_flights = 0
    state_or_country = set()
    with open("all_flights.tsv", "w", newline="") as outf:
        writer = csv.writer(outf, delimiter="\t", lineterminator="\n")
        writer.writerow(headers)
        for year in years:
            for month in month_range:
                for day in day_range:
                    if month == 2 and day > 28:
                        continue
                    if month in [4, 6, 9, 11] and day == 31:
                        continue
                    if date(year, month, day) < date(2023, 4, 17):
                        continue
                    today = date.today()
                    if today < date(year, month, day):
                        break
                    try:
                        flight_data_path = get_arrivals(day, month, year)
                    except:
                        print(f"no data for {year}-{month}-{day}")
                        continue

                    with open(flight_data_path, newline="") as csvfile:
                        reader = csv.DictReader(csvfile)

                        for row in reader:
                            origin = row["Origin"]
                            airport_code = row["Origin Code"]
                            dep_time = row["Departure Time"]
                            arr_time = row["Arrival Time"]
                            dep_date = row["Departure Date"]
                            arr_date = row["Arrival Date"]
                            scheduled_arr_time = row["Scheduled Arrival Time"]
                            scheduled_arr_date = row["Scheduled Arrival Date"]
                            terminal = row["Terminal"]
                            equipment = row["Equipment"]
                            flight = row["Flight"]
                            airline = row["Airline"]
                            status = row["Status"]
                            if "DIVERTED" in status:
                                flight_exclusions["Diverted"] += 1
                                continue
                            elif "Canceled" in status:
                                flight_exclusions["Canceled"] += 1
                                continue
                            elif "En Route" in status:
                                flight_exclusions["En Route"] += 1
                                continue
                            elif "Unknown" in status:
                                if (
                                    arr_time == scheduled_arr_time
                                    and arr_date == scheduled_arr_date
                                ):  
                                    pass # flight seems fine
                                else:
                                    flight_exclusions["Unknown status, irregular arrival time"] += 1 
                                    continue # Requires further investigation
                            if airport_code in us_codes:
                                location = us_codes[airport_code]
                                if location == "La":
                                    location = "LA"
                                try:
                                    state = state_code_dict[location]
                                except:
                                    state = None
                                total_origin_counts[state] += 1
                                country = "United States"
                            elif airport_code in non_us_codes:
                                location = non_us_codes[airport_code]
                                total_origin_counts[location] += 1
                                country = location
                                state = None
                            elif (
                                airport_code not in us_codes
                                and airport_code not in non_us_codes
                            ):
                                try:
                                    location = airports_not_in_sheet[
                                        airport_code
                                    ]
                                    if location == "Dominican Republic":
                                        country = "Dominican Republic"
                                        state = None
                                        total_origin_counts[country] += 1
                                    elif (
                                        location == "Turks and Caicos Islands"
                                    ):
                                        country = "Turks and Caicos Islands"
                                        state = None
                                        total_origin_counts[country] += 1
                                    else:
                                        country = "United States"
                                        state = state_code_dict[location]
                                        total_origin_counts[state] += 1
                                except:
                                    # print(
                                    # f"Airport code {airport_code} not covered"
                                    # )
                                    missing_airport_codes[airport_code] += 1
                                    flight_exclusions[
                                        "Missing Airport Code"
                                    ] += 1
                                    continue

                            if not arr_time:
                                flight_exclusions[
                                    "No Arrival Time provided"
                                ] += 1
                                continue

                            raw_departure_datetime = datetime.strptime(
                                f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M"
                            )

                            if state is not None:
                                departure_time_zone = time_zone_dict[state]
                            else:
                                departure_time_zone = time_zone_dict[country]

                            tz_adjusted_departure_datetime = (
                                raw_departure_datetime.replace(
                                    tzinfo=ZoneInfo(departure_time_zone)
                                )
                            )

                            raw_arrival_datetime = datetime.strptime(
                                f"{arr_date} {arr_time}", "%Y-%m-%d %H:%M"
                            )
                            tz_adjusted_arrival_datetime = (
                                raw_arrival_datetime.replace(
                                    tzinfo=ZoneInfo("America/New_York")
                                )
                            )

                            flight_time = (
                                tz_adjusted_arrival_datetime
                                - tz_adjusted_departure_datetime
                            )
                            raw_flight_time = (
                                raw_arrival_datetime - raw_departure_datetime
                            )
                            flight_hours = flight_time.total_seconds() / 3600
                            if flight_hours < 0:
                                flight_exclusions["Negative Flight Time"] += 1
                                continue
                            if flight_hours > 19:
                                flight_exclusions[
                                    "Flight Time longer than 19 hours"
                                ] += 1
                                continue
                            included_flights += 1
                            flight_hours = round(flight_hours) 
                            plot_flight_times[flight_hours] += 1
                            writer.writerow(
                                [
                                    origin,
                                    airport_code,
                                    arr_date,
                                    terminal,
                                    equipment,
                                    flight,
                                    airline,
                                    country,
                                    state,
                                    flight_time,
                                ]
                            )
    for key, value in flight_exclusions.items():
        print(f"{key}: {value}")
    print(f"Included flights: {included_flights}")
    with open("total_origin_counts.tsv", "w") as f:
        for location, flight_count in total_origin_counts.items():
            f.write(f"{location}\t{flight_count}\n")
    print(plot_flight_times)
    with open("total_hour_counts.tsv", "w") as f:
        for location, flight_time in total_hour_counts.items():
            f.write(f"{location}\t{flight_time}\n")
    missing_airport_codes = dict(
        sorted(
            missing_airport_codes.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    plt.show()


def start():
    create_all_flights_tsv()


if __name__ == "__main__":
    start()
