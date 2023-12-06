#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime


def time_to_float(t):
    return t.hour + t.minute / 60 + t.second / 3600


def create_df():
    df = pd.read_csv(
        "all_flights.tsv",
        delimiter="\t",
        names=[
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
        ],
    )

    flight_hour_counts = defaultdict(int)
    flight_counts = defaultdict(int)
    location_types = {}

    count = 0
    for _, row in df.iterrows():
        # turn the string into a datetime object

        try:
            flight_time = datetime.strptime(row["Flight Time"], "%H:%M:%S")
        except:
            print(f"conversion of time {row['Flight Time']} failed")
            count += 1
            continue
        flight_length = time_to_float(flight_time)

        if row["Nation"] == "United States":
            location = row["State"]
            location_type = "US State"
        else:
            location = row["Nation"]
            location_type = "Country"
        flight_hour_counts[location] += flight_length
        flight_counts[location] += 1
        location_types[location] = location_type

    flight_hour_count_df = pd.DataFrame(
        list(flight_hour_counts.items()), columns=["Location", "Count"]
    )
    flight_hour_count_df["Type"] = flight_hour_count_df["Location"].map(
        location_types
    )
    flight_hour_count_df = flight_hour_count_df.sort_values(
        by="Count", ascending=False
    )

    top_30_flight_hour_locations = flight_hour_count_df.head(30)

    flight_count_df = pd.DataFrame(
        list(flight_counts.items()), columns=["Location", "Count"]
    )

    flight_count_df["Type"] = flight_count_df["Location"].map(location_types)

    flight_count_df = flight_count_df.sort_values(by="Count", ascending=False)

    top_30_flight_count_locations = flight_count_df.head(30)

    return top_30_flight_hour_locations, top_30_flight_count_locations


def create_barplot(top_30, title, xlim):
    plt.figure(figsize=(10, 9))
    colors = [
        "#80b1d3" if loc_type == "US State" else "#fb8072"
        for loc_type in top_30["Type"]
    ]
    for i in range(0, xlim, xlim // 7):
        plt.axvline(x=i, color="black", alpha=0.2, zorder=0)

    plt.barh(top_30["Location"], top_30["Count"], color=colors, zorder=3)
    plt.ylabel("Location")
    plt.xlabel(f"Number of {title}")
    plt.title(f"Top 30 US States and Non-US Countries by total {title}")
    plt.xticks(rotation=0)
    plt.tick_params(
        axis="y",
        which="both",
        left=False,
        right=False,
    )
    plt.yticks(rotation=0)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().yaxis.set_label_text("")
    plt.tight_layout()
    plt.savefig(f"top-30-{title}.png", dpi=600)


def start():
    top_30_hours, top_30_flights = create_df()
    create_barplot(top_30_hours, "flight hours", 70000)
    create_barplot(top_30_flights, "flights", 14000)


if __name__ == "__main__":
    start()
