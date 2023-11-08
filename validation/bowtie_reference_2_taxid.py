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
from get_alignment_sample import return_sam_records

sam_records = return_sam_records()


refs = sam_records["ref"].value_counts().index.tolist()


df = pd.read_csv("ncbi-fetch-metadata.txt", sep="\t")

fname_2_taxid = {}
with open("ncbi-fetch-metadata.txt", mode="r", newline="") as inf:
    reader = csv.DictReader(inf, delimiter="\t")
    for row in reader:
        taxid = row["taxid"]
        local_fname = row["local_filename"]
        stripped_fname = os.path.basename(local_fname).removesuffix(".gz")
        fname_2_taxid[stripped_fname] = taxid


genome_id_2_taxid = {}
for reference in glob.glob("raw-genomes/*.fna"):
    with open(reference) as inf:
        for reference_entry in Bio.SeqIO.parse(inf, "fasta"):
            genome_id = reference_entry.id
            reference_fname = os.path.basename(reference)
            taxid = fname_2_taxid[reference_fname]
            genome_id_2_taxid[genome_id] = taxid


for ref in refs:
    try:
        taxid = genome_id_2_taxid[ref]
        print(taxid)
    except:
        print(f"{ref} was not in dictionary")
