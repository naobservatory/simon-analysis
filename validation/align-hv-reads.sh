#!/usr/bin/env bash

set -e # exit on error 

ROOT_DIR="$PWD"
if [ "$(basename $PWD)" != "validation" ]; then
    echo "Must be run from validation directory"
    exit 1
fi


if [ ! -e target_projects_and_samples.json ]; then
    $ROOT_DIR/return_bioprojects.py
fi  

json_file=$ROOT_DIR/target_projects_and_samples.json
# creating and populating hvreads directory, based on target_projects_and_samples.json
if [ ! -d hvreads ]; then
    mkdir hvreads
    for bucket in nao-mgs nao-restricted; do
        for bioproject in $(jq -r 'keys[]' $json_file); do
            for sample in $(jq -r ".[\"$bioproject\"][]" $json_file); do

                echo s3://$bucket/${bioproject}/hvreads/${sample}.hvreads.json
            done
        done
    done | xargs -P 32 -I {} aws s3 cp {} hvreads/ 
fi
# Creating fastq files, based on hvreads Kraken assignment (first value after each key in *.hvreads.json). Creates pair1, pair2, and combined fastq files.
if [ ! -d hvfastqs ]; then
    mkdir hvfastqs
    ls hvreads | \
        xargs -P 32 -I {} \
              $ROOT_DIR/json_to_hv_assignment_fasta.py hvreads hvfastqs {}
fi
# Checks all kraken matches in *hvreads.json, returning those that match human viruses, as detailed in ~/code/mgs-pipeline/human-viruses.tsv 
if [ ! -e observed-human-virus-taxids.txt ]; then
    $ROOT_DIR/determine_hv_assignment_taxids.py \
        hvreads/ \
        ${ROOT_DIR}/../mgs-pipeline/human-viruses.tsv \
	observed-human-virus-taxids.txt
fi

# Creates detailed-taxids.txt, hv_taxid_to_detailed.json, refseq/viral/*, and ncbi-fetch-metadata.txt
$ROOT_DIR/get_genomes.py


if [ ! -d raw-genomes ]; then
    mkdir raw-genomes
    for x in $(find refseq/ | grep gz$); do
        gunzip -c "$x" > raw-genomes/$(basename ${x/.fna.gz/.fna})
    done
fi

if [ ! -e human-viruses.1.bt2 ]; then
        ${ROOT_DIR}/../../bowtie2-2.5.1-macos-arm64/bowtie2-build \
	-f \
        --threads 32 \
        $(find raw-genomes/ | grep .fna$ | tr '\n' ',') \
        human-viruses
fi

if [ ! -e hvsams ]; then
    mkdir hvsams
    $ROOT_DIR/run_bowtie2.py
fi
