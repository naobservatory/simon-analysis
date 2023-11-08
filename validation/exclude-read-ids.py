#!/usr/bin/env python
from return_sam_records import sam_records
import pandas as pd


def start():
    df = sam_records()

    dropped_merged = df[
        (df["read_type"] == "combined") & (df["log_length_adj_score"] < 22)
    ]["read_id"].tolist()

    dropped_pair_low_score = (
        df[df["read_type"].str.startswith("read_")]
        .groupby("read_id")
        .filter(lambda x: (x["log_length_adj_score"].max() < 22))["read_id"]
        .tolist()
    )

    excluded_reads_set = set(dropped_merged + dropped_pair_low_score)

    with open("simon-excluded-read-ids.txt", "w") as outf:
        for read in excluded_reads_set:
            outf.write(f"{read}\n")


if __name__ == "__main__":
    start()
