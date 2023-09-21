#!/usr/bin/env python3


import os
import json

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


def start():
    target_bio_projects = {}
    for study in studies:
        if study in [
            "Johnson 2023",  # unpublished data
            "Cui 2023",  # untreated undigested sludge
            "Wang 2022",  # COVID-19 hospital wastewater
            "Petersen 2015",  # air plane waste
            "Hendriksen 2019",  # man hole"
            "Moritz 2019",  # university wastewater
            "Wu 2020",  # lung sample
            "Fierer 2022",  # university campus
        ]:
            continue

        for bioproject in metadata_papers[study]["projects"]:
            samples = metadata_bioprojects[bioproject]

            if study == "Bengtsson-Palme 2016":
                samples = [
                    sample
                    for sample in samples
                    if metadata_samples[sample]["fine_location"].startswith("Inlet")
                ]

            if study == "Ng 2019":
                samples = [
                    sample
                    for sample in samples
                    if metadata_samples[sample]["fine_location"] == "Influent"
                ]

            # if target_bio_projects[bioproject] doesn't exist, create it
            if bioproject not in target_bio_projects:
                target_bio_projects[bioproject] = []

            target_bio_projects[bioproject].extend(samples)
    with open("target_projects_and_samples.json", "w") as outf:
        json.dump(target_bio_projects, outf, indent=2)


if __name__ == "__main__":
    start()
