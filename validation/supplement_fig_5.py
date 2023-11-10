#!/usr/bin/env python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from return_sam_records import sam_records


def start():
    df = sam_records()
    FIGURE_SIZE = (8, 5)

    sns.histplot(
        data=df,
        x="log_length_adj_score",
        bins=100,
        color="#fe9929",
        element="bars",
        legend=False,
    )

    plt.title("Log(read length) adjusted Alignment Scores (Target Studies)")
    plt.xlabel("Normalized Alignment Score")
    plt.ylabel("Frequency")
    sns.despine(
            right=True, top=True)
    plt.axvline(x=22, color="black", linestyle="--")
    plt.savefig("supplement_fig_5.png", dpi=600)
    plt.clf()


if __name__ == "__main__":
    start()
