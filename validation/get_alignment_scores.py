#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
from math import sqrt

directory_path = "hvsams"

length_adjusted_alignment_scores = []
if os.path.exists(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".sam"):
            with open(directory_path + "/" + filename) as inf:
                for line in inf:
                    if line.startswith("@"):
                        continue
                    else:
                        line = line.split("\t")
                        alignment_score = int(line[11].split(":")[2])
                        read_length = len(line[9])

                        length_adjusted_alignment_scores.append(
                            alignment_score / sqrt(read_length)
                        )


plt.hist(length_adjusted_alignment_scores, bins=100)
plt.show()
plt.clf()
