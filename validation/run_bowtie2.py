#!/usr/bin/env python3

import glob
import os.path
import subprocess
from collections import defaultdict

samples = defaultdict(dict)
for fastq in glob.glob("hvfastqs/*.fastq"):
    sample, category, _ = os.path.basename(fastq).rsplit(".", 2)
    samples[sample][category] = fastq

for sample, fastqs in sorted(samples.items()):
    out = "hvsams/%s.sam" % sample
    if os.path.exists(out):
        continue

    cmd = [
        "/Users/simongrimm/code/bowtie2-2.5.1-macos-arm64/bowtie2",
        "-x",
        "human-viruses",
        "--very-sensitive",
        "--score-min",
        "L,-0.6,-0.6",
        "--threads",
        "24",
        "-S",
        out,
    ]
    assert ("pair1" in fastqs) == ("pair2" in fastqs)
    if "pair1" in fastqs:
        cmd.extend(["-1", fastqs["pair1"], "-2", fastqs["pair2"]])
    if "combined" in fastqs:
        cmd.extend(["-U", fastqs["combined"]])

    try:
        subprocess.check_call(cmd)
    except Exception:
        print(" ".join(cmd))
        raise
