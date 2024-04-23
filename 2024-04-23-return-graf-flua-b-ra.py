#!/usr/bin/env python3

import pandas as pd


df_graf_various = pd.read_csv('graf_np_ct_mgs.tsv', sep='\t', skiprows=1)


df_graf_various["relative_abundance"] = None

def rpkm_to_ra(df):
    genome_lengths_in_kb = {
        "Influenza A": 13.5,
        "Influenza B": 14.5,
        "Metapneumovirus": 13.3,
        "Rhinovirus": 7.2,
        "Parainfluenzavirus 1": 15.5,
        "Parainfluenzavirus 3": 15.5,
        "Parainfluenzavirus 4": 17.4,
        "Respiratory Syncytial Virus": 15.2
    }



    for virus, virus_length in genome_lengths_in_kb.items():
        df.loc[df["Virus"] == virus, "relative_abundance"] = df.loc[df["Virus"] == virus, "RPKM"] * virus_length / 1e6


    df_graf_influenza = df_graf_various[(df_graf_various["Virus"] == "Influenza A") | (df_graf_various["Virus"] == "Influenza B")]
    df_graf_influenza["relative_abundance"] = df_graf_influenza["relative_abundance"].apply(lambda x: f"{x:.0e}")

    return df_graf_influenza

df_graf_influenza = rpkm_to_ra(df_graf_various)
df_graf_influenza.to_csv('graf_np_flu_ra.tsv', sep='\t', index=False)




