#!/usr/bin/env python
from return_hv_taxid_dict import hv_taxid_dict
from return_sam_records import sam_records
import return_hv_taxid_dict
import pandas as pd
import csv
import glob
import Bio.SeqIO
import os


def genomeid_2_taxid_dict() -> dict:
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

    return genome_id_2_taxid


def start():
    hv_records = hv_taxid_dict()
    df = sam_records()
    mapping_dict = genomeid_2_taxid_dict()

    print(df["ref"])

    if "ref" not in df.columns:
        print("'ref' column not found in DataFrame.")
        return

    # maybe remove
    df = df[df["ref"].notna()]

    df.apply(lambda x: print(mapping_dict[x["ref"]]), axis=1)

    df.apply(lambda x: print(hv_records[x["ref"]]), axis=1)

    # df.filter(
    #     lambda x: dict[x["ref"]] == hv_records[x["ref"]],
    # )

    # if df["read_type"] == "combined":
    #     print("combined")


if __name__ == "__main__":
    start()
