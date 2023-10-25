#!/usr/bin/env python3

import sys
import glob
import json

hvreads_dir, human_viruses, taxids_out = sys.argv[1:]

hv_taxids = set()  # strings
seen_hv_taxids = set()  # ints

with open(human_viruses) as inf:
    for line in inf:
        taxid = line.split("\t")[0]
        hv_taxids.add(taxid)

# print(hv_taxids)
for fname in glob.glob("%s/*.json" % hvreads_dir):
    with open(fname) as inf:
        for kraken_assignment, _, *_ in json.load(inf).values():
            if str(kraken_assignment) in hv_taxids:
                seen_hv_taxids.add(kraken_assignment)

with open(taxids_out, "w") as outf:
    for taxid in sorted(seen_hv_taxids):
        outf.write("%s\n" % taxid)
