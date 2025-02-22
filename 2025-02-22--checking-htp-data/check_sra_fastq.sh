#!/bin/bash

# Usage function
usage() {
    echo "Usage: $0 <accession_list_file>"
    echo "Checks the first read ID of each SRA accession"
    echo ""
    echo "Example:"
    echo "  $0 SRR_Acc_List.txt"
    exit 1
}

# Create output file
OUTPUT_FILE="sra_content.txt"

# Initialize output file with timestamp
echo "SRA FASTQ Content Check - $(date)" > "$OUTPUT_FILE"
echo "=================================" >> "$OUTPUT_FILE"

# Check if argument is provided
if [ $# -ne 1 ]; then
    usage
fi

ACCESSION_FILE="$1"
TEMP_DIR="temp"

# Check if input file exists
if [ ! -f "$ACCESSION_FILE" ]; then
    echo "Error: Cannot find accession list file: $ACCESSION_FILE" | tee -a "$OUTPUT_FILE"
    exit 1
fi

# Check if fastq-dump is installed
if ! command -v fastq-dump &> /dev/null; then
    echo "Error: fastq-dump not found. Please install SRA Toolkit" | tee -a "$OUTPUT_FILE"
    exit 1
fi

# Create temp directory
mkdir -p "$TEMP_DIR"

# Process each accession
echo "Reading accessions from $ACCESSION_FILE:" | tee -a "$OUTPUT_FILE"
cat "$ACCESSION_FILE" | tee -a "$OUTPUT_FILE"
echo "------------------------" | tee -a "$OUTPUT_FILE"

while read -r accession; do
    # Skip empty lines
    [ -z "$accession" ] && continue

    echo "Starting to process accession: $accession" | tee -a "$OUTPUT_FILE"

    # Create and move to accession-specific directory
    mkdir -p "$TEMP_DIR/$accession"
    cd "$TEMP_DIR/$accession" || exit 1

    # Download just 1 read using fastq-dump
    if ! fastq-dump --split-3 --gzip -X 1 "$accession" 2>/dev/null; then
        echo "Error downloading $accession" | tee -a "../../$OUTPUT_FILE"
        cd - >/dev/null || exit 1
        continue
    fi

    # Check each fastq file that exists
    for fastq_file in *.fastq.gz; do
        if [ -f "$fastq_file" ]; then
            echo "$fastq_file" | tee -a "../../$OUTPUT_FILE"
            if command -v gzcat &> /dev/null; then
                gzcat "$fastq_file" | head -n 2 | tee -a "../../$OUTPUT_FILE"
            else
                zcat "$fastq_file" | head -n 2 | tee -a "../../$OUTPUT_FILE"
            fi
            echo "---" | tee -a "../../$OUTPUT_FILE"
            rm "$fastq_file"
        fi
    done

    # Cleanup
    cd - >/dev/null || exit 1
    rm -rf "$TEMP_DIR/$accession"

    echo "------------------------" | tee -a "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done < "$ACCESSION_FILE"

# Final cleanup
rm -rf "$TEMP_DIR"

echo "Done! Results saved to $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"