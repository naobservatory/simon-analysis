#! /usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pe_lengths = pd.read_csv(
    "pe_length_stats.tsv.gz", sep="\t"
)  # from s3://nao-mgs-simon/test_paired_end/output/results/qc_length_stats.tsv.gz
se_lengths = pd.read_csv(
    "se_length_stats.tsv.gz", sep="\t"
)  # from s3://nao-mgs-simon/test_single_read/output/results/qc_length_stats.tsv.gz


fig, ax = plt.subplots(dpi=300, figsize=(10, 4))
sns.lineplot(
    data=pe_lengths,
    x="length",
    y="n_sequences",
    ax=ax,
    units="sample",
    estimator=None,
    legend=True,
)
ax.grid(True, linestyle="--", alpha=0.7)

sns.lineplot(
    data=se_lengths,
    x="length",
    y="n_sequences",
    ax=ax,
    units="sample",
    estimator=None,
    legend=True,
)


ax.set_xlabel("Read length")
ax.set_ylabel("Number of sequences")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("read_length_ont_se_pe.png")
