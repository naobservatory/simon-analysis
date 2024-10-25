#! /usr/bin/env python3
import gzip
import os
import pandas as pd
import sys
from multiprocessing import Pool

def start():
    fwd_reads = pd.read_csv("fwd_read_files.tsv", sep="\t")
    tasks = []
    for dates, group in fwd_reads.groupby(["date"]):
        date, = dates
        files = group["file"].tolist()
        for direction in ["_1.fastq", "_2.fastq"]:
            direction_files = files
            if direction == "_2.fastq":
                direction_files = [file.replace("_1.fastq", "_2.fastq") for file in files]
            concat_file = f"/home/ec2-user/mnt/nao-mgs-simon/uci-sra-upload/HTP-{date}{direction}.gz"
            tasks.append((direction_files, concat_file))

    with Pool(16) as p:
        p.map(concat_files, tasks)


def concat_files(args):
    direction_files, concat_file = args
    print(f"Concatenating {direction_files} into {concat_file}")

    with gzip.open(concat_file, 'wt') as concat_file:
        for file in direction_files:

            local_file = file.replace("s3://", "/home/ec2-user/mnt/")
            with gzip.open(local_file, 'rt') as f:
                for line in f:
                    concat_file.write(line)

if __name__ == '__main__':
    start()