#!/usr/bin/env python3

import pandas as pd


n_reads = (
    152254  # length of seq file divided by four (each read has four lines)
)


dict_taxid = {
    0: "assigned",
    9606: "human",
    2: "bacteria",
    10239: "viruses",
}

with open("cladecounts-2024-06/NAO-ONT-20240912-DCS_RNA3.tsv", "r") as inf:
    for row in inf:
        taxid, dir_assigned, dir_hits, clade_assigned, clade_hits = (
            row.strip().split("\t")
        )
        taxid = int(taxid)
        if taxid in dict_taxid:
            n_reads_taxid = int(clade_hits)
            ra = f"{(n_reads_taxid / n_reads) * 100:.2f}%"
            id_taxid = dict_taxid[taxid]
            print(
                "%s (%s) were assigned to %s" % (n_reads_taxid, ra, id_taxid)
            )
