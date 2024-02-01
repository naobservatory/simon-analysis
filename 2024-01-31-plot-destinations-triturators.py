#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import ast

def time_to_float(time):
    time = time.strip() 
    try:
        time_object = dt.datetime.strptime(time, "%H:%M:%S")
        hours = (
            time_object.hour
            + time_object.minute / 60
            + time_object.second / 3600
        )
        return hours
    except Exception as e:
        print(f"conversion of time {time} failed: {e}")
        return 0

def return_flights():
    with open("all_flights.tsv") as infile:
        lines = infile.readlines()        
        us_flights = []
        lines = lines[1:]
        for line in lines:
            origin, origin_code, date, terminal, equipment, flight, airline, nation, state, flight_time = line.split("\t")
            airlines = ast.literal_eval(airline) 
            prime_airline = airlines[0]
            if nation == "Canada":
                triturator_status = "Unknown"
            elif prime_airline in [
                "United Airlines",
                "American Airlines"]:
                triturator_status = "American Airlines\nTriturator"

            elif prime_airline in [
                "JetBlue Airways",
                "Delta Air Lines",
                    "Southwest Airlines"]:
                triturator_status = "Swissport\nTriturator"

            elif prime_airline in [ #Swissport Ground Handling
                'Porter Airlines', 
                'LATAM Airlines', 
                'Hawaiian Airlines', 
                'BermudAir', 
                'Korean Air', 
                'Iberia', 
                'Fly Play', 
                'SAS Scandinavian Airlines', 
                'Qatar Airways', # Closest match to 'Qatar'
                'Qatar Executive', # Also a match for 'Qatar'
                'TAP Air Portugal', 
                'Turkish Airlines', 
                'Hainan Airlines', 
                'El Al Israel Airlines', 
                'Aer Lingus', 
                'ITA Airways', 
                'Condor']:
                triturator_status = "Swissport\nTriturator"

            elif nation != "United States":
                triturator_status = "Swissport\nTriturator"
        
            else:
                triturator_status = "Unknown"
 
            us_flights.append([origin, origin_code, date, terminal, equipment, flight, airline, nation, state, flight_time, triturator_status])

        us_flights_df = pd.DataFrame(us_flights)
        # set headers
        us_flights_df.columns = ["Origin", "Origin Code", "Date", "Terminal", "Equipment", "Flight", "Airline", "Nation", "State", "Flight Time", "Triturator Status"]

        return us_flights_df 


def return_plotting_df():
    df = return_flights()

    df["Flight Hours"] = df["Flight Time"].apply(time_to_float)

    df["Plotting Origin"] = np.where(
        df["Nation"] == "United States",
        df["State"],
        df["Nation"],
    )

    df = (
        df.groupby(["Plotting Origin", "Triturator Status"])
        .agg({"Flight Hours": "sum"})
        .reset_index()

    )

    df = df.pivot(
        index="Plotting Origin", columns="Triturator Status", values="Flight Hours"
    )

    df["Total"] = df.sum(axis=1)
    df = df.sort_values(by="Total", ascending=False)
    df = df.drop("Total", axis=1)

    return df


def origin_to_nation_dict():
    df = return_flights()
    df["Plotting Origin"] = np.where(
        df["Nation"] == "United States",
        df["State"],
        df["Nation"],
    )
    nation_dict = df.set_index("Plotting Origin")["Nation"].to_dict()
    return nation_dict

def return_destination_trit_plot():
    df = return_plotting_df()
    nation_dict = origin_to_nation_dict()

    df = df.head(50)
    fig, ax = plt.subplots(figsize=(8, 7))
    df.plot.barh(stacked=True, ax=ax, width=0.8)

    
    for i, label in enumerate(ax.get_yticklabels()):
        origin = label.get_text()
        if nation_dict[origin] != "United States":
            label.set_color("darkred")
            label.set_weight("bold")


    # drop legend title
    ax.get_legend().set_title("")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.tick_params(axis="y", which="both", left=False, right=False)
    plt.ylabel("")
    plt.xlabel("Total Flight Hours")
    plt.title("Total Flight Hours per Country/State and Triturator (Top 50)")

    plt.tight_layout()
    plt.savefig("triturator_destination_flight_hours.png", dpi=600)





def start():
    return_destination_trit_plot()




if __name__ == "__main__":
    start()
