#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

    df = df[
        df["Terminal"].isin(["A", "B", "C", "E"])
    ]  # Terminals that aren't in this list have less than 15 flights each

    df = (
        df.groupby(["Plotting Origin", "Terminal"])
        .size()
        .reset_index(name="Count")
    )

    df = df.pivot(index="Plotting Origin", columns="Terminal", values="Count")
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
    print(nation_dict)
    return nation_dict


def create_barplot():
    df = return_plotting_df()
    nation_dict = origin_to_nation_dict()

    df = df.head(40)
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
    plt.xlabel("Number of flights")
    plt.tight_layout()
    plt.savefig("terminal_breakdown.png", dpi=600)


def start():
    create_barplot()


if __name__ == "__main__":
    start()
