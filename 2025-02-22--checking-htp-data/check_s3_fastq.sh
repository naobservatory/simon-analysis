#!/bin/bash

# Create a temporary directory and output file
TEMP_DIR="temp_s3_check"
OUTPUT_FILE="s3_content.txt"
mkdir -p "$TEMP_DIR"

# Initialize output file with timestamp
echo "S3 FASTQ Content Check - $(date)" > "$OUTPUT_FILE"
echo "=================================" >> "$OUTPUT_FILE"

# Function to check first read ID of a gzipped fastq file
check_fastq() {
    local url="$1"
    local filename=$(basename "$url")

    # Download first 50KB of the file (should be plenty for first read)
    if ! curl -s -f -L "$url" --range 0-51200 > "$TEMP_DIR/$filename"; then
        echo "Error: Failed to download $filename" | tee -a "$OUTPUT_FILE"
        return 1
    fi

    # Print filename and get first read ID and sequence (first two lines after @)
    echo "$filename" | tee -a "$OUTPUT_FILE"
    if command -v gzcat &> /dev/null; then
        gzcat "$TEMP_DIR/$filename" 2>/dev/null | awk '/^@/{print;getline;print;exit}' | tee -a "$OUTPUT_FILE"
    else
        zcat "$TEMP_DIR/$filename" 2>/dev/null | awk '/^@/{print;getline;print;exit}' | tee -a "$OUTPUT_FILE"
    fi

    # Clean up
    rm -f "$TEMP_DIR/$filename"
    echo "---" | tee -a "$OUTPUT_FILE"
}

# Array of URLs to check
URLS=(
    "https://sra-pub-src-1.s3.amazonaws.com/SRR31712294/HTP-2024-01-15-part-1_1.fastq.gz.1"
    "https://sra-pub-src-1.s3.amazonaws.com/SRR31712294/HTP-2024-01-15-part-1_2.fastq.gz.1"
    "https://sra-pub-src-1.s3.amazonaws.com/SRR31712294/HTP-2024-01-15-part-2_1.fastq.gz.1"
    "https://sra-pub-src-1.s3.amazonaws.com/SRR31712294/HTP-2024-01-15-part-2_2.fastq.gz.1"
)

# Process each URL
for url in "${URLS[@]}"; do
    check_fastq "$url"
done

# Final cleanup
rm -rf "$TEMP_DIR"

echo "Done! Results saved to $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"