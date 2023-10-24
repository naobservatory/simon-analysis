#!/usr/bin/env python
import pysam
import os
import json
import matplotlib.pyplot as plt
from math import sqrt
import pandas as pd


dashboard = os.path.expanduser("~/code/mgs-pipeline/dashboard/")

with open(os.path.join(dashboard, "human_virus_sample_counts.json")) as inf:
    human_virus_sample_counts = json.load(inf)

with open(os.path.join(dashboard, "metadata_samples.json")) as inf:
    metadata_samples = json.load(inf)

with open(os.path.join(dashboard, "metadata_bioprojects.json")) as inf:
    metadata_bioprojects = json.load(inf)

with open(os.path.join(dashboard, "metadata_papers.json")) as inf:
    metadata_papers = json.load(inf)

with open(os.path.join(dashboard, "taxonomic_names.json")) as inf:
    taxonomic_names = json.load(inf)


studies = list(metadata_papers.keys())


def return_sam_records():
    sam_records = []

    hvsams_directory_path = "hvsams"

    for filename in os.listdir(hvsams_directory_path):
        sam_file = pysam.AlignmentFile(hvsams_directory_path + "/" + filename, "r")
        for read in sam_file.fetch():
            read_id = read.query_name
            flag = (
                read.flag
            )  # https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml#:~:text=all%20applicable%20flags.-,Flags,-relevant%20to%20Bowtie
            if flag < 64:
                read_type = "combined"
            elif flag > 64 and flag < 128:
                read_type = "read_1"
            elif flag > 128:
                read_type = "read_2"
            sequence = read.query_sequence
            read_length = read.query_length
            try:
                alignment_score = read.get_tag("AS")
                length_adj_score = alignment_score / sqrt(read_length)
                sam_records.append(
                    [
                        read_id,
                        sequence,
                        alignment_score,
                        length_adj_score,
                        flag,
                        read_type,
                    ]
                )
            except:
                alignment_score = 0
                length_adj_score = 0

                sam_records.append(
                    [
                        read_id,
                        sequence,
                        alignment_score,
                        length_adj_score,
                        flag,
                        read_type,
                    ]
                )

    df = pd.DataFrame(
        sam_records,
        columns=[
            "read_id",
            "sequence",
            "alignment_score",
            "length_adj_score",
            "flag",
            "read_type",
        ],
    )

    return df


def start():
    df = return_sam_records()
    dropped_merged = df[
        (df["read_type"] == "combined") & (df["length_adj_score"] < 10)
    ]["read_id"].tolist()

    dropped_non_merged = (
        df[df["read_type"].str.startswith("read_")]
        .groupby("read_id")
        .filter(lambda x: (x["length_adj_score"].max() < 10))
    )["read_id"].to_list()

    print(dropped_merged + dropped_non_merged)


if __name__ == "__main__":
    start()
