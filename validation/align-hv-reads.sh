#!/usr/bin/env bash

json_file=~/code/simons-public-notebook/target_projects_and_samples.json

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

if [ ! -d hvfastqs ]; then
    mkdir hvfastqs
    ls hvreads | \
        xargs -P 32 -I {} \
              ~/code/simons-public-notebook/json_to_fasta.py hvreads hvfastqs {}
fi

if [ ! -e observed-human-virus-taxids.txt ]; then
    ~/code/simons-public-notebook/determine_hv_taxids.py \
        hvreads/ \
        ~/code/mgs-pipeline/human-viruses.tsv \
        observed-human-virus-taxids.txt
fi

~/code/simons-public-notebook/get_genomes.py



if [ ! -d raw-genomes ]; then
    mkdir raw-genomes
    for x in $(find refseq/ | grep gz$); do
        zcat "$x" > raw-genomes/$(basename ${x/.fna.gz/.fna})
    done
fi

if [ ! -e human-viruses.1.bt2 ]; then
    ~/code/bowtie2-2.5.1-macos-arm64/bowtie2-build \
        -f \
        --threads 32 \
        $(find raw-genomes/ | grep .fna$ | tr '\n' ',') \
        human-viruses
fi

if [ ! -e hvsams ]; then
    mkdir hvsams
    ~/code/simons-public-notebook/run_bowtie2.py
fi