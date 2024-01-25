#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import ast


def return_processed_df():
    full_df = pd.read_csv('weather-data.csv')
    df = full_df[['NAME', 'DATE', 'PRCP']].copy()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['PRCP'].fillna(0, inplace=True) 
    
    df['PRCP_Smoothed'] = df.groupby('NAME')['PRCP'].rolling(window=7, center=True).mean().reset_index(level=0, drop=True)
    return df.reset_index()

def plot_rainfall(weekly_data):
    plt.figure(figsize=(10, 3))
    df = weekly_data 
    stations = df['NAME'].unique()
    skipped_stations = 0
    for station in stations:
        station_data = df[df['NAME'] == station]
        if len(station_data) < 150: #stations with little data create a lot of noise
            print("Skipping station: ", station)
            skipped_stations += 1 
            continue
        plt.plot(station_data['DATE'], station_data['PRCP_Smoothed'], label=station, color='grey', linewidth=1)

    mean_line = df.groupby('DATE')['PRCP_Smoothed'].mean().reset_index()
    plt.plot(mean_line['DATE'], mean_line['PRCP_Smoothed'], label='Mean', color='red', linewidth=2)
    print("Skipped stations: ", skipped_stations/len(stations))
    
    for i in range(1, 8):
        plt.axhline(y=i/5, color='grey', linestyle='-', linewidth=0.5, alpha=0.5, zorder=0)
    plt.xlabel('Date')
    plt.ylabel('')
    plt.title('Average Daily Rainfall in counties covered by MWRA (7-day rolling average, inches)')
    plt.savefig('rainfall.png', bbox_inches='tight', dpi=600)
    plt.show()

def start():
    weekly_data = return_processed_df()
    plot_rainfall(weekly_data)


if __name__ == '__main__':
    start()
