#!/usr/bin/env python
import pysam
import os
import matplotlib.pyplot as plt
from math import sqrt
import pandas as pd


def sam_records():
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
            ref = sam_file.get_reference_name(read.reference_id)
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
                        ref,
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
                        ref,
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
            "ref",
        ],
    )
    return df


def start():
    return sam_records()


if __name__ == "__main__":
    start()
