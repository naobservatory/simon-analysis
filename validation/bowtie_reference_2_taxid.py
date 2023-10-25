#!/usr/bin/env python3
import csv
import os
import glob
import json
import pandas as pd
import pysam
import Bio.SeqIO
from collections import Counter
import matplotlib.pyplot as plt


sam_records = []

hvsams_directory_path = "hvsams"

for filename in os.listdir(hvsams_directory_path):
    sam_file = pysam.AlignmentFile(hvsams_directory_path + "/" + filename, "r")
    for read in sam_file.fetch():
        read_id = read.query_name
        sequence = read.query_sequence
        read_length = read.query_length
        ref = sam_file.get_reference_name(read.reference_id)
        try:
            alignment_score = read.get_tag("AS")
            length_adj_score = alignment_score / sqrt(read_length)
            sam_records.append([read_id, sequence, alignment_score, length_adj_score])
        except:
            alignment_score = 0
            length_adj_score = 0

            sam_records.append(
                [read_id, sequence, alignment_score, length_adj_score, ref]
            )
df = pd.DataFrame(
    sam_records,
    columns=["read_id", "sequence", "alignment_score", "length_adj_score", "ref"],
)

refs = df["ref"].value_counts().index.tolist()


df = pd.read_csv("ncbi-fetch-metadata.txt", sep="\t")


fname_genome_id_pairs = []
for reference in glob.glob("raw-genomes/*.fna"):
    with open(reference) as inf:
        for reference_entry in Bio.SeqIO.parse(inf, "fasta"):
            genome_id = reference_entry.id

            reference_fname = os.path.basename(reference)
            # if reference_fname is not a key in fname_2_genome_id, create it:
            fname_genome_id_pairs.append((reference_fname, genome_id))

genome_id_2_taxid = {}
with open("ncbi-fetch-metadata.txt", mode="r", newline="") as inf:
    reader = csv.DictReader(inf, delimiter="\t")
    for row in reader:
        taxid = row["taxid"]
        local_fname = row["local_filename"]
        stripped_fname = os.path.basename(local_fname).removesuffix(".gz")
        genome_id = fname_2_genome_id[stripped_fname]
        print(genome_id)
        if len(genome_id) > 1:
            for id in genome_id:
                genome_id_2_taxid[id] = taxid
        else:
            genome_id_2_taxid[genome_id] = taxid

# see this code by ChatGPT that would fix a lot:
import csv

genome_id_2_taxid = {}

with open("ncbi-fetch-metadata.txt", mode="r", newline="") as inf:
    reader = csv.DictReader(inf, delimiter="\t")

    for row in reader:
        taxid = row["taxid"]
        local_fname = row["local_filename"]
        stripped_fname = os.path.basename(local_fname).removesuffix(".gz")

        # Here we filter out the tuples that match the current file name
        matching_genome_ids = [
            genome_id
            for (fname, genome_id) in fname_genome_id_pairs
            if fname == stripped_fname
        ]

        if matching_genome_ids:
            for genome_id in matching_genome_ids:
                genome_id_2_taxid[genome_id] = taxid
        else:
            print(f"No genome ID found for file {stripped_fname}")


for ref in refs:
    try:
        taxid = genome_id_2_taxid[ref]
        print(taxid)
    except:
        print(f"{ref} was not in dictionary")


# let's say we have a given


# def process_sam(fname):
#     sample = os.path.basename(fname)
#     with pysam.AlignmentFile(fname, "r") as sam:
#         for record in sam:
#             ref = sam.get_reference_name(record.reference_id)
#             ref_seq = genomes[ref]
#             qry_seq = record.query_sequence
#             ref_pos = record.reference_start

#             longest_alignment = max(
#                 [length for category, length in record.cigartuples if category == 0],
#                 default=0,
#             )
#             longest_soft_clip = max(
#                 [length for category, length in record.cigartuples if category == 4],
#                 default=0,
#             )
#             all_soft_clipped = sum(
#                 [length for category, length in record.cigartuples if category == 4]
#             )

#             score = record.get_tag("AS") / (len(qry_seq) - all_soft_clipped)

#             if longest_soft_clip < 30 or longest_alignment < 30:
#                 continue

#             print(
#                 "%.2f" % (score),
#                 longest_soft_clip,
#                 longest_alignment,
#                 record.query_name,
#             )


# for paper in metadata["papers"]:
#     if "Rothman" not in paper:
#         continue
#     for bioproject in metadata["papers"][paper]["projects"]:
#         for sample in metadata["bioprojects"][bioproject]:
#             if metadata["samples"][sample].get("enrichment", "") == "panel":
#                 continue

#             fname = "hvsams/%s.sam" % sample
#             if os.path.exists(fname):
#                 process_sam(fname)
