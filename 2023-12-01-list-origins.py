#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from math import sqrt


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
    month_range = range(4, 13)
    day_range = range(1, 32)
    arrivals_dict = defaultdict(int)

    for month in month_range:
        for day in day_range:
            try:
                flight_data_path = get_arrivals(day, month)
            except:
                print("No arrivals for %s-%s" % (month, day))
                continue
            with open(flight_data_path) as arrivals:
                next(arrivals)
                for line in arrivals:
                    origin_city = line.split(",")[0]
                    if origin_city.isdigit():
                        origin_city = line.split(",")[1]

                    arrivals_dict[origin_city] += 1

    with open("arrivals.tsv", "w") as tsv:
        for key, value in arrivals_dict.items():
            tsv.write("%s\t%s\n" % (key, value))


def start():
    plot_flight_origins()


if __name__ == "__main__":
    start()
