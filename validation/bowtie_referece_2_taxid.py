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

# metadata = {}
# for fname in ["papers", "bioprojects", "samples"]:
#     with open(
#         "/Users/jeffkaufman/code/mgs-pipeline/dashboard/metadata_%s.json" % fname
#     ) as inf:
#         metadata[fname] = json.load(inf)

# genomes = {}
# for genome in glob.glob("raw-genomes/*.fna"):
#     with open(genome) as inf:
#         for record in Bio.SeqIO.parse(inf, "fasta"):
#             genome_id = record.id
#             print(genome)


sam_file = pysam.AlignmentFile("hvsams/ERR1467145.sam", "r")

# for record in sam_file.fetch():
#     ref = sam_file.get_reference_name(record.reference_id)
#     # print(ref)

for record in sam_file:
    ref = sam_file.get_reference_name(record.reference_id)
    # print(ref)

df = pd.read_csv("ncbi-fetch-metadata.txt", sep="\t")


# def bowtie_reference_to_taxid():
reference_to_taxid_dict = {}  # NC_* -> taxid


taxid_2_fname = {}
taxid_fnames = []
with open("ncbi-fetch-metadata.txt", mode="r", newline="") as inf:
    reader = csv.DictReader(inf, delimiter="\t")
    for row in reader:
        taxid = row["taxid"]
        local_fname = row["local_filename"]
        stripped_fname = os.path.basename(local_fname).removesuffix(".gz")
        print(taxid)
        print(stripped_fname)
        taxid_2_fname[taxid] = stripped_fname
        taxid_fnames.append(stripped_fname)

genome_fnames = []
genome_id_2_taxid = {}
for reference in glob.glob("raw-genomes/*.fna"):
    with open(reference) as inf:
        for reference_entry in Bio.SeqIO.parse(inf, "fasta"):
            genome_id = reference_entry.id
            reference_fname = os.path.basename(reference)
            # genome_id_2_taxid[genome_id] = taxid_2_fname[reference_fname]
            genome_fnames.append(reference_fname)

print(len(taxid_fnames))
print(len(genome_fnames))


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
