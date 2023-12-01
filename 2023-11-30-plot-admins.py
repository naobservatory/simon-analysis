#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
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
    # https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.76.zip
    cities_data = pd.read_csv("worldcities.csv")
    cities = cities_data["city_ascii"].values

    unknown_counts = defaultdict(int)
    total_origin_counts = defaultdict(int)

    day_range = range(1, 10)
    plot_size = round(sqrt(len(day_range)))

    fig, axs = plt.subplots(plot_size, plot_size, figsize=(10, 10))
    axs = axs.flatten()
    colors = lambda i: plt.colormaps["tab20"](i / 16)

    MONTH = 11  # November
    for day, ax in zip(day_range, axs):
        flight_data_path = get_arrivals(day, MONTH)
        flight_data = pd.read_csv(flight_data_path)
        per_day_origin_counts = defaultdict(int)
        for origin_city in flight_data["Origin"].values:
            if origin_city not in cities:
                try:
                    administrative_area = cities_not_in_worldcities[
                        origin_city
                    ]
                    per_day_origin_counts[administrative_area] += 1
                except:
                    per_day_origin_counts["Unknown"] += 1
                    total_origin_counts["Unknown"] += 1
                unknown_counts[origin_city] += 1
                total_origin_counts[administrative_area] += 1
            else:
                administrative_area = cities_data[
                    cities_data["city_ascii"] == origin_city
                ][["admin_name"]].values[0][0]
                per_day_origin_counts[administrative_area] += 1
                total_origin_counts[administrative_area] += 1
        df = pd.DataFrame(
            list(per_day_origin_counts.items()), columns=["location", "count"]
        )
        df = df.sort_values(by=["count"], ascending=False)

        new_index = df.index.max() + 1
        CUT_OFF = 15

        df = df[:CUT_OFF]
        # sum_lower_locations = sum(df["count"][CUT_OFF:])

        # df.loc[new_index] = ["Other", sum_lower_locations]
        x = range(len(df["location"]))

        ax.bar(x, df["count"])
        ymin, ymax = ax.get_ylim()
        for i in range(int(ymin), int(ymax), 20):
            ax.axhline(i, color="black", alpha=0.1, zorder=1)
        for i in x:
            ax.bar(i, df["count"].iloc[i], color=colors(i), zorder=2)
        ax.set_title(f"2023-11-{day:02d} Flight Origins")
        ax.set_xticks([])

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colors(i)) for i in range(len(df))
    ]
    labels = [df["location"].iloc[i] for i in range(len(df))]

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2)
    plt.legend(
        handles,
        labels,
        ncol=5,
        bbox_to_anchor=(0.7, -0.05),
    )
    plt.show()


def start():
    plot_flight_origins()


if __name__ == "__main__":
    start()
