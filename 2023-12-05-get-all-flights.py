#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
import csv
from collections import defaultdict

from datetime import datetime, date

airports_not_in_sheet = {
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


def get_state_code_dict():
    state_code_dict = {}
    with open("state_code_to_name.tsv", mode="r", encoding="utf-8") as file:
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
                    print(fine_location)
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


def get_flight_duration():
    us_codes, non_us_codes = get_airport_codes()
    state_code_dict = get_state_code_dict()
    if "LHR" in non_us_codes:
        print("LHR in non_us_codes")
    else:
        print("LHR not in non_us_codes")
    month_range = range(4, 13)
    day_range = range(1, 32)

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
                    print(f"no data for {month}-{day}")
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
                        terminal = row["Terminal"]
                        equipment = row["Flight"]
                        flight = row["Flight"]
                        airline = row["Airline"]

                        if not arr_time:
                            # print("Flight en route or cancelled")
                            # print(row)
                            continue
                        departure_datetime = datetime.strptime(
                            f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M"
                        )
                        arrival_datetime = datetime.strptime(
                            f"{arr_date} {arr_time}", "%Y-%m-%d %H:%M"
                        )

                        flight_time = arrival_datetime - departure_datetime
                        if airport_code in us_codes:
                            location = us_codes[airport_code]
                            if location == "La":
                                location = "LA"
                            try:
                                state = state_code_dict[location]
                            except:
                                print(f"{location} not in state_code_dict")
                                print(row)
                                state = "N/A"
                            total_origin_counts[state] += 1
                            country = "United States"
                        elif airport_code in non_us_codes:
                            location = non_us_codes[airport_code]
                            total_origin_counts[location] += 1
                            country = location
                            state = "N/A"
                        elif (
                            airport_code not in us_codes
                            and airport_code not in non_us_codes
                        ):
                            try:
                                location = airports_not_in_sheet[airport_code]
                                if location == "Dominican Republic":
                                    country = "Dominican Republic"
                                    state = "N/A"
                                    total_origin_counts[country] += 1
                                elif location == "Turks and Caicos Islands":
                                    country = "Turks and Caicos Islands"
                                    state = "N/A"
                                    total_origin_counts[country] += 1
                                else:
                                    country = "United States"
                                    state = state_code_dict[location]
                                    total_origin_counts[state] += 1
                            except:
                                print(
                                    f"Airport code {airport_code} not covered"
                                )
                                missing_airport_codes[airport_code] += 1
                                continue

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
    with open("total_origin_counts.tsv", "w") as f:
        for location, flight_count in total_origin_counts.items():
            f.write(f"{location}\t{flight_count}\n")
    missing_airport_codes = dict(
        sorted(
            missing_airport_codes.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    print(missing_airport_codes)


def start():
    get_flight_duration()


if __name__ == "__main__":
    start()
