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
    plt.hist(df[df["length_adj_score"] != 0]["length_adj_score"], bins=100)
    plt.title("Length-adjusted Alignment Scores")
    plt.xlabel("Alignment Score")
    plt.ylabel("Frequency")
    plt.savefig("length_adj_scores.png", dpi=300)
    plt.clf()


if __name__ == "__main__":
    start()
