import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, linregress
from typing import List
from collections import namedtuple
from collections import defaultdict


DOUBLING_PERIOD_D = 3
DEBUG = None


def logit(x):
    return np.log(x / (1 - x))


def logistic(x):
    return 1 / (1 + np.exp(-x))


def get_studies():
    df_op_lu = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/lu_op_ct_mgs.tsv",
        sep="\t",
        skiprows=1,
    )  # Data obtained from Table S1.
    df_op_lu.rename(
        columns={"SCV-2 Relative Abundance": "scv2_ra", "Ct value": "scv2_ct"},
        inplace=True,
    )
    df_op_lu[["patient_status", "swab_type", "Study"]] = [
        "Inpatient",
        "op",
        "Lu et al. 2021",
    ]

    df_np_rodriguez = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/rodriguez_np_ct_mgs.csv", sep=";"
    )  # Data sent to us by authors.
    rodriguez_patient_status_dict = {
        "Hospit": "Inpatient",
        "Out_Patient": "Outpatient",
        "Intensive_Care": "ICU",
    }
    df_np_rodriguez["patient_status"] = df_np_rodriguez["Group"].replace(
        rodriguez_patient_status_dict
    )
    df_np_rodriguez["scv2_ra"] = (
        df_np_rodriguez["Reads_2019_CoV"] / df_np_rodriguez["Reads_Total"]
    )

    df_np_rodriguez.rename(columns={"CoV_Ct_number": "scv2_ct"}, inplace=True)
    df_np_rodriguez[["swab_type", "Study"]] = ["np", "Rodriguez et al. 2021"]

    df_np_babiker = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/babiker_np_ct_mgs.tsv",
        sep="\t",
        skiprows=1,
    )  # Data obtained from table S2
    df_np_babiker.rename(
        columns={
            "SARS-CoV-2 RT-PCR Ct": "scv2_ct",
            "SARS-CoV-2 RA": "scv2_ra",
            "Inpatient/ED vs. Outpatient": "patient_status",
        },
        inplace=True,
    )
    df_np_babiker["scv2_ct"] = (
        df_np_babiker["scv2_ct"].replace(",", ".", regex=True).astype(float)
    )
    df_np_babiker["patient_status"] = df_np_babiker["patient_status"].apply(
        lambda x: x if x in ["Inpatient", "Outpatient"] else "Unknown"
    )
    # The data uses . to represent missing data. Set this column to integers, while at the same time mapping missing data to NA.
    df_np_babiker["days_from_onset"] = (
        df_np_babiker["Day of Testing Relative to Symptom Onset"]
        .replace(".", "-1")
        .astype(int)
        .replace(-1, "NA")
    )
    df_np_babiker[["swab_type", "Study"]] = ["np", "Babiker et al. 2020"]

    df_np_mostafa = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/mostafa-np-ra-ct.tsv", sep="\t"
    )  # Data obtained from Table S2.
    mostafa_severity_dict = {
        1: "Required\nventilator",
        2: "ICU",
        3: "Inpatient",
        4: "Outpatient",
        0: "Unknown",
    }
    df_np_mostafa.rename(
        columns={
            "SARS-CoV-2 RT-PCR Ct value": "scv2_ct",
            "CosmosID Proportion Mapped to SARS-CoV-2": "scv2_ra",
        },
        inplace=True,
    )
    df_np_mostafa["Severity index"] = df_np_mostafa["Severity index"].replace(
        "–", 0
    )
    df_np_mostafa["patient_status"] = (
        df_np_mostafa["Severity index"]
        .astype(int)
        .replace(mostafa_severity_dict)
    )
    # There is no information of why some patients only have "<7" as their days from onset. We set it to 3.5 (the average of 1-6 days.)
    df_np_mostafa["days_from_onset"] = df_np_mostafa[
        "No. of days from onset"
    ].replace({"–": "NA", "<7": "3.5"})
    # Drop samples unless we have both qPCR and MGS detection
    df_np_mostafa = df_np_mostafa[df_np_mostafa["COVID-19-positive"] == True]
    df_np_mostafa = df_np_mostafa[df_np_mostafa["scv2_ct"] != "–"]
    df_np_mostafa["scv2_ct"] = df_np_mostafa["scv2_ct"].astype(float)
    df_np_mostafa[["swab_type", "Study"]] = ["np", "Mostafa et al. 2020"]

    study_dfs = {
        "Lu et al. 2021": df_op_lu,
        "Babiker et al. 2020": df_np_babiker,
        "Mostafa et al. 2020": df_np_mostafa,
        "Rodriguez et al. 2021": df_np_rodriguez,
    }

    return study_dfs


def adjust_cts(df):
    np_data = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/2024-06-18-np-nasal-ct.tsv",
        sep="\t",
        skiprows=1,
    )
    np_means = np_data.mean()

    NP_ADJUSTMENT_FACTOR = np_means.mean()
    goodall_data = pd.read_csv(
        "data/2024-06-17-swab-sensitivity/goodall-op-nasal-ct.tsv",
        sep="\t",
        skiprows=2,
        header=None,
    )
    OP_ADJUSTMENT_FACTOR = goodall_data[0].mean()

    df["adjusted_scv2_ct"] = df["scv2_ct"]
    # Subtract the adjustment factors from the CT values (NP_ADJUSTMENT_FACTOR is negative, so it increases the CT values)
    df.loc[df["swab_type"] == "np", "adjusted_scv2_ct"] -= NP_ADJUSTMENT_FACTOR
    df.loc[df["swab_type"] == "op", "adjusted_scv2_ct"] -= OP_ADJUSTMENT_FACTOR

    return df


def adjust_rel_abun(composite_df):
    composite_df = composite_df.copy()
    composite_df.loc[:, "scv2_ra_logit"] = composite_df["scv2_ra"].apply(logit)

    slope, intercept, r_value, p_value, std_err = linregress(
        composite_df["scv2_ct"], composite_df["scv2_ra_logit"]
    )
    composite_df["adjusted_scv2_ra_logit"] = (
        intercept + slope * composite_df["adjusted_scv2_ct"]
    )
    residuals = composite_df["scv2_ra_logit"] - (
        intercept + slope * composite_df["scv2_ct"]
    )

    sigma_squared = np.var(residuals, ddof=2)

    sigma = np.sqrt(sigma_squared)

    noise = np.random.normal(loc=0, scale=sigma, size=len(composite_df))

    composite_df["adjusted_scv2_ra_logit_with_noise"] = (
        composite_df["adjusted_scv2_ra_logit"] + noise
    )
    composite_df["adjusted_scv2_ra"] = composite_df[
        "adjusted_scv2_ra_logit_with_noise"
    ].apply(logistic)
    return composite_df


def get_adjusted_composite_ras():
    study_dfs = get_studies().values()

    composite_df = pd.concat(study_dfs)
    composite_df = composite_df[
        composite_df["patient_status"].isin(["Inpatient", "Outpatient"])
    ]
    zero_ras = composite_df[composite_df["scv2_ra"] == 0]["scv2_ra"].tolist()
    df = adjust_cts(composite_df)
    df_w_o_zeros = df[df["scv2_ra"] != 0]
    df_w_o_zeros = adjust_rel_abun(df_w_o_zeros)
    ras = df_w_o_zeros["adjusted_scv2_ra"].tolist() + zero_ras
    sorted_ras = sorted(ras)
    formatted_ras = [f"{ra:.0e}" if ra != 0 else "0" for ra in sorted_ras]

    return formatted_ras


def generate_html_string(ras):
    str = ""
    for i, ra in enumerate(ras):
        if i == 0:
            i + 1
            str += '"' + ra + " "
            continue
        elif ((i - 1) % 9 == 0) and ((i - 1) != 0):
            str += '"' + ra + " "
            continue
        elif i % 9 == 0:
            str += ra + ' " +\n'
            continue
        str += ra + " "
        if i == len(adjusted_composite_ras) - 1:
            str += '";'


adjusted_composite_ras = get_adjusted_composite_ras()
str = generate_html_string(adjusted_composite_ras)
print(str)
