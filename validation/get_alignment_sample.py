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
            sequence = read.query_sequence
            read_length = read.query_length
            try:
                alignment_score = read.get_tag("AS")
                length_adj_score = alignment_score / sqrt(read_length)
                sam_records.append(
                    [read_id, sequence, alignment_score, length_adj_score]
                )
            except:
                alignment_score = 0
                length_adj_score = 0

                sam_records.append(
                    [read_id, sequence, alignment_score, length_adj_score]
                )
    df = pd.DataFrame(
        sam_records,
        columns=["read_id", "sequence", "alignment_score", "length_adj_score"],
    )
    return df


def start():
    df = return_sam_records()

    LOW_CUT_OFF = 4
    HIGH_CUT_OFF = 25
    MID_CUT_OFF = 15

    low_sample = df[df["length_adj_score"].round() == LOW_CUT_OFF].sample(
        n=10, random_state=1
    )

    mid_sample = df[df["length_adj_score"].round() == MID_CUT_OFF].sample(
        n=10, random_state=1
    )
    # get shape of length_adj_score_5_sub_sample

    high_sample = df[df["length_adj_score"].round() == HIGH_CUT_OFF].sample(
        n=10, random_state=1
    )

    concatenated_samples = pd.concat([low_sample, mid_sample, high_sample])

    # Save the data to a CSV file
    concatenated_samples.to_csv("alignment_sample.csv", index=False)

    zero_score_samples = df[df["length_adj_score"] == 0].sample(n=10, random_state=1)

    zero_score_samples.to_csv("zero_score_samples.csv", index=False)


if __name__ == "__main__":
    start()
