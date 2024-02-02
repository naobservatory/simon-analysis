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


target_taxa = {
    10239: ("viruses", "Viruses"),
    2731341: ("duplodnaviria", "DNA Viruses"),
    2732004: ("varidnaviria", "DNA Viruses"),
    2731342: ("monodnaviria", "DNA Viruses"),
    2842242: ("ribozyviria", "RNA Viruses"),
    687329: ("anelloviridae", "DNA Viruses"),
    2559587: ("riboviria", "RNA Viruses"),
    2840022: ("adnaviria", "DNA Viruses"),
    9999999999: ("human viruses", "Viruses"),
}


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

    while current_rank != "family":
        current_taxid = parent_taxid
        try:
            current_rank, parent_taxid = parents[current_taxid]
        except KeyError:
            print(f"Taxid {current_taxid} not found in parents")

    else:
        family_taxid = current_taxid

        return family_taxid


def get_taxid_name(
    target_taxid: int, taxonomic_names: dict[str, list[str]]
) -> str:
    tax_name = taxonomic_names[f"{target_taxid}"][0]
    return tax_name


def assemble_plotting_dfs() -> tuple[pd.DataFrame, pd.DataFrame]:

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
                    if sample_type != "hvac_filter":
                        continue
                    if season not in [
                        "Winter",
                        "Spring",
                        "Summer",
                        "Fall",
                        "Closed",
                    ]:
                        continue
                humanreads = "%s.humanviruses.tsv" % sample

                if not os.path.exists(f"humanviruses/{humanreads}"):
                    print(
                        "Downloading %s from %s" % (humanreads, bioproject),
                        flush=True,
                    )
                    subprocess.check_call(
                        [
                            "aws",
                            "s3",
                            "cp",
                            "s3://nao-mgs/%s/humanviruses/%s"
                            % (bioproject, humanreads),
                            "humanviruses/",
                        ]
                    )

                with open(f"humanviruses/{humanreads}") as inf:
                    human_virus_counts = {}
                    human_virus_reads = 0

                    for line in inf:
                        (
                            line_taxid,
                            assignments,
                            _,
                        ) = line.strip().split("\t")
                        assignments = int(assignments)
                        line_taxid = line_taxid

                        human_virus_counts[line_taxid] = assignments
                        human_virus_reads += assignments

                    bar_plot_data.append(
                        {
                            "study": study,
                            "sample": sample,
                            "na_type": na_type,
                            **human_virus_counts,
                        }
                    )

    df = pd.DataFrame(bar_plot_data)
    species_taxids = df.columns[3:]
    parents = load_taxonomic_data()
    species_to_family = {
        taxid: get_family(int(taxid), parents) for taxid in species_taxids
    }

    df.rename(columns=species_to_family, inplace=True)
    df = df.groupby(df.columns, axis=1).sum() #summing family counts
    df = df.melt(
        id_vars=["study", "sample", "na_type"],
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
    # get total reads for each na_type and study
    #total_reads_list = []

    #df = df.drop(columns=["taxid", "reads"])
    
    print(df)
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
    
    total_reads_per_study = df.groupby(["study", "na_type"]).reads.sum().reset_index()



    print(total_reads_per_study)
    df_pivot = df.pivot_table(index=['study', 'na_type'], 
                              columns='hv_family', 
                              values='relative_abundance')



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

    sns.despine(top=True, right=True, left=True, bottom=False)
    plt.tight_layout()
    plt.savefig("barplot.png", bbox_inches="tight", dpi=300)
    return ax


def save_plot(fig, figdir: Path, name: str) -> None:
    for ext in ["pdf", "png"]:
        fig.savefig(figdir / f"{name}.{ext}", bbox_inches="tight", dpi=900)


def start():
    # parent_dir = Path("..")
    # figdir = Path(parent_dir / "figures")
    # figdir.mkdir(exist_ok=True)

    # boxplot_df, barplot_df = assemble_plotting_dfs()

    # fig = plt.figure(
    #    figsize=(9, 11),
    # )

    # gs = GridSpec(2, 2, height_ratios=[9, 7], figure=fig)

    # boxplot_ax = boxplot(
    #    fig.add_subplot(gs[0, :]),
    #    boxplot_df,
    # )

    # study_order = [text.get_text() for text in boxplot_ax.get_yticklabels()]

    # barplot(fig.add_subplot(gs[1, :]), barplot_df, study_order)

    # plt.tight_layout()
    # save_plot(fig, figdir, "composite_fig_1")
    df = assemble_plotting_dfs()
    barplot(df)
    parents = load_taxonomic_data()
    # print(parents[3050295])


if __name__ == "__main__":
    start()
