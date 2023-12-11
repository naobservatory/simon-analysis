#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt


def time_to_float(time):
    try:
        time_object = dt.datetime.strptime(time, "%H:%M:%S")
        hours = (
            time_object.hour
            + time_object.minute / 60
            + time_object.second / 3600
        )
        return hours
    except:
        print(f"conversion of time {time} failed")
        return 0


def return_df():
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
    return df


def return_plotting_df():
    df = return_df()

    df["Plotting Origin"] = np.where(
        df["Nation"] == "United States",
        df["State"],
        df["Nation"],
    )

    df["Flight Hours"] = df["Flight Time"].apply(lambda x: time_to_float(x))

    df = (
        df.groupby(["Plotting Origin"])
        .agg({"Flight Hours": "sum"})
        .reset_index()
    )
    df = df.sort_values("Flight Hours", ascending=False)
    df.set_index("Plotting Origin", inplace=True)

    return df


def origin_to_nation_dict():
    df = return_df()
    df["Plotting Origin"] = np.where(
        df["Nation"] == "United States",
        df["State"],
        df["Nation"],
    )
    nation_dict = df.set_index("Plotting Origin")["Nation"].to_dict()
    return nation_dict


def create_barplot():
    df = return_plotting_df()
    nation_dict = origin_to_nation_dict()

    df = df.head(50)
    f, ax = plt.subplots(figsize=(8, 7))
    df.plot.barh(ax=ax, width=0.8)

    for i, bar in enumerate(ax.patches):
        origin = df.index[i]
        if nation_dict.get(origin) != "United States":
            bar.set_color("red")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.tick_params(axis="y", which="both", left=False, right=False)
    plt.ylabel("")
    plt.xlabel("Total Flight Hours")
    plt.title("Total Flight Hours per Country/State (Top 50)")
    plt.legend().remove()
    plt.tight_layout()
    plt.savefig("flight_hours_per_nation.png", dpi=600)


def start():
    create_barplot()


if __name__ == "__main__":
    start()
