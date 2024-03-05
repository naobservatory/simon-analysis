#!/usr/bin/env python3

import gzip
import json
import os
import subprocess
import typing
from pathlib import Path

import matplotlib.pyplot as plt  # type: ignore
import matplotlib.ticker as ticker  # type: ignore
import numpy as np
import pandas as pd
import seaborn as sns  # type: ignore
from matplotlib.gridspec import GridSpec  # type: ignore
from collections import defaultdict
from scipy import stats

dashboard = os.path.expanduser("~/code/mgs-pipeline/dashboard/")


with open(os.path.join(dashboard, "human_virus_sample_counts.json")) as inf:
    human_virus_sample_counts = json.load(inf)

with open(os.path.join(dashboard, "metadata_samples.json")) as inf:
    metadata_samples = json.load(inf)

with open(os.path.join(dashboard, "metadata_bioprojects.json")) as inf:
    metadata_bioprojects = json.load(inf)

with open(os.path.join(dashboard, "metadata_papers.json")) as inf:
    metadata_papers = json.load(inf)

with open(os.path.join(dashboard, "taxonomic_names.json")) as inf:
    taxonomic_names = json.load(inf)

studies = list(metadata_papers.keys())

def load_taxonomic_data() -> dict[int, tuple[str, int]]:
    parents = {}
    with open(os.path.join(dashboard, "nodes.dmp")) as inf:
        for line in inf:
            child_taxid, parent_taxid, child_rank, *_ = line.replace(
                "\t|\n", ""
            ).split("\t|\t")
            parent_taxid = int(parent_taxid)
            child_taxid = int(child_taxid)
            child_rank = child_rank.strip()
            parents[child_taxid] = (child_rank, parent_taxid)
    return parents




def get_family(taxid: int, parents: dict[int, tuple[str, int]]) -> int:
    original_taxid = taxid
    try:
        current_rank, parent_taxid = parents[original_taxid]
    except KeyError:
        print(f"Taxid {original_taxid} not found in parents")
        return None
    max_tries = 15
    tries=0
    while current_rank != "family":
        if tries > max_tries: 
            print(f"Reached max tries for taxid {original_taxid}")
            return None
        current_taxid = parent_taxid 
        try:
            current_rank, parent_taxid = parents[current_taxid]
        except KeyError:
            print(f"Taxid {current_taxid} not found in parents")
        tries += 1
    else:
        family_taxid = current_taxid

        return family_taxid

def test_get_family():
    parents = load_taxonomic_data()
    assert get_family(11676, parents) == 11632 
    assert get_family(694009, parents) == 11118 
    print("get_family tests passed!") 

def get_taxid_name(
    target_taxid: int, taxonomic_names: dict[str, list[str]]
) -> str:
    tax_name = taxonomic_names[f"{target_taxid}"][0]
    return tax_name

def assemble_plotting_dfs() -> tuple[pd.DataFrame, pd.DataFrame]:
    parents = load_taxonomic_data() #DEBUG

    sample_ras = defaultdict(list)
    bar_plot_data = []
    for study in studies:
        if study not in ["Prussin 2019", "Rosario 2018"]:
            continue 
        for bioproject in metadata_papers[study]["projects"]:
            samples = metadata_bioprojects[bioproject]

            for sample in samples:

                na_type = metadata_samples[sample]["na_type"]
                if study == "Prussin 2019":
                    sample_type = metadata_samples[sample]["sample_type"]
                    season = metadata_samples[sample]["season"]
                    sampling_range = metadata_samples[sample]["sampling_range"] 

                    
                    if sample_type != "hvac_filter":
                        continue
                    if "Control" in sampling_range or "Unexposed" in sampling_range: 
                        print(f"Excluding {sample} due to it being a control")
                        continue
                    if season not in [
                        "Winter",
                        "Spring",
                        "Summer",
                        "Fall",
                        "Closed",
                    ]:
                        continue
                human_virus_counts = {} 
                human_virus_reads = 0
                for taxid in human_virus_sample_counts.keys():
                    n_assignments = human_virus_sample_counts[taxid].get(sample, 0)
                    human_virus_counts[taxid] = n_assignments 
                    human_virus_reads += n_assignments

                bar_plot_data.append(
                    {
                        "study": study,
                        "sample": sample,
                        "na_type": na_type,
                        "hv_reads": human_virus_reads,
                        **human_virus_counts,
                    }
                )
                
    df = pd.DataFrame(bar_plot_data)
    species_taxids = df.columns[4:]
    parents = load_taxonomic_data()
    species_to_family = {
        taxid: get_family(int(taxid), parents) for taxid in species_taxids
    }

    df.rename(columns=species_to_family, inplace=True)
    df = df.groupby(df.columns, axis=1).sum() # summing family counts
    df = df.melt(
        id_vars=["study", "sample", "na_type", "hv_reads"],
        var_name="taxid",
        value_name="reads",
    )
    df = df.groupby(["study", "na_type", "taxid"]).reads.sum().reset_index()
    df = df[df.reads != 0]
    df["relative_abundance"] = df.groupby(["study", "na_type"])[
        "reads"
    ].transform(lambda x: x / x.sum())
    N_TOP_TAXA = 9
    top_taxa = (
        df.groupby("taxid").relative_abundance.sum().nlargest(N_TOP_TAXA).index
    )
    top_taxa_rows = df[df.taxid.isin(top_taxa)]
    top_taxa_rows["hv_family"] = top_taxa_rows["taxid"].apply(
        lambda x: get_taxid_name(x, taxonomic_names)
    )

    minor_taxa = df[~df.taxid.isin(top_taxa)]["taxid"].unique()
    minor_taxa_rows = (
        df[df.taxid.isin(minor_taxa)]
        .groupby(["study", "na_type"])
        .agg(
            {
                "relative_abundance": "sum",
            }
        )
    ).reset_index()
    minor_taxa_rows["hv_family"] = "minor_taxa"
    
    df = pd.concat([top_taxa_rows, minor_taxa_rows])
    return df


def barplot(df):
    ten_color_palette = [
        "#8dd3c7",
        "#f1c232",
        "#bebada",
        "#fb8072",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#bc80bd",
        "#d9d9d9",
    ]
    
    reads_per_study_and_na = df.groupby(["study", "na_type"]).reads.sum().reset_index()

    reads_per_study_and_na = list(reads_per_study_and_na.itertuples(index=False, name=None))
    df_pivot = df.pivot_table(index=['study', 'na_type'], 
                              columns='hv_family', 
                              values='relative_abundance')


    # drop brackets from bar labels
    fig, ax = plt.subplots(figsize=(10, 5))
    df_pivot.plot(kind='barh', stacked=True, color=ten_color_palette, ax=ax) 

    ax.invert_yaxis()

    ax.set_xlabel("Relative abundance among human-infecting virus families")

    ax.tick_params(left=False)

    ax.set_ylabel("")
    ax.tick_params(left=False, labelright=True, labelleft=False)
    ax.set_xlim(right=1, left=0)

    ax.legend(
        loc=(0.035, -0.72),
        ncol=4,
        fontsize=11.1,
        frameon=False,
    )
    y_positions = [0.87, 0.63, 0.37, 0.13] # FIXME: hardcoded
    for ypos, (study, na_type, reads) in zip(y_positions, reads_per_study_and_na):
        ax.text(-0.02, ypos, f"{int(reads)} reads", transform=ax.transAxes, fontsize=11.1, ha="right", va="center")

    sns.despine(top=True, right=True, left=True, bottom=False)
    plt.tight_layout()
    plt.savefig("barplot_json.png", bbox_inches="tight", dpi=300)
    return ax


def save_plot(fig, figdir: Path, name: str) -> None:
    for ext in ["pdf", "png"]:
        fig.savefig(figdir / f"{name}.{ext}", bbox_inches="tight", dpi=900)


def start():
    df = assemble_plotting_dfs()
    # run test
    test_get_family()
    barplot(df)


if __name__ == "__main__":
    start()
