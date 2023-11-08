#!/usr/bin/env python
import matplotlib.pyplot as plt


from return_sam_records import sam_records


def start():
    df = sam_records()
    fig, axs = plt.subplots(2, 1, tight_layout=True)

    df[df["read_type"] == "combined"]["length_adj_score"].plot.hist(
        ax=axs[0], bins=100, alpha=0.5, label="combined"
    )
    df[df["read_type"] == "read_1"]["length_adj_score"].plot.hist(
        ax=axs[1], bins=100, alpha=0.5, label="read_1"
    )

    for ax in axs:
        ax.legend(loc="upper right")

    plt.savefig("combined_vs_read1.png")


if __name__ == "__main__":
    start()
