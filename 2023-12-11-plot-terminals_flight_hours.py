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

    df = df[
        df["Terminal"].isin(["A", "B", "C", "E"])
    ]  # Terminals that aren't in this list have less than 15 flights each

    df = (
        df.groupby(["Plotting Origin", "Terminal"])
        .agg({"Flight Hours": "sum"})
        .reset_index()
    )
    # log (base 10) all flight hours

    df = df.pivot(
        index="Plotting Origin", columns="Terminal", values="Flight Hours"
    )
    df["Total"] = df.sum(axis=1)
    df = df.sort_values("Total", ascending=False)
    df = df.drop("Total", axis=1)

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
    df.plot.barh(stacked=True, ax=ax, width=0.8)

    for i, label in enumerate(ax.get_yticklabels()):
        origin = label.get_text()
        if nation_dict[origin] != "United States":
            label.set_color("darkred")
            label.set_weight("bold")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.tick_params(axis="y", which="both", left=False, right=False)
    plt.ylabel("")
    plt.xlabel("Total Flight Hours")
    plt.title("Total Flight Hours per Country/State and Terminal (Top 50)")

    plt.tight_layout()
    plt.savefig("terminal_flight_hours_breakdown.png", dpi=600)


def start():
    create_barplot()


if __name__ == "__main__":
    start()
