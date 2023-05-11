#!/bin/bash

# Input and output paths
INPUT_S3_PATH="s3://alucloud/76/SRR24441101.fastq.gz"
OUTPUT_S3_PATH="s3://alucloud/76/preprocessed/"
LOCAL_INPUT_FILE="/data/input.fastq.gz"
LOCAL_INPUT_UNZIPPED_FILE="/data/input.fastq"
LOCAL_OUTPUT_FILE="/data/output.fastq"
LOCAL_OUTPUT_ZIPPED_FILE="/data/output.fastq.gz"

# Create /data directory
mkdir -p /data

# Download the input file from S3
aws s3 cp "$INPUT_S3_PATH" "$LOCAL_INPUT_FILE"

# Unzip the input file
gzip -d "$LOCAL_INPUT_FILE"

# Run FastQC for quality control
fastqc -o /data/ "$LOCAL_INPUT_UNZIPPED_FILE"

# Run Trimmomatic for adapter trimming
trimmomatic SE -phred33 \
  "$LOCAL_INPUT_UNZIPPED_FILE" \
  "$LOCAL_OUTPUT_FILE" \
  ILLUMINACLIP:/usr/local/share/trimmomatic/adapters/Trimmomatic-0.39/adapters/NexteraPE-PE.fa:2:30:10 \
  LEADING:3 \
  TRAILING:3 \
  SLIDINGWINDOW:4:15 \
  MINLEN:36

# Zip the preprocessed output file
gzip "$LOCAL_OUTPUT_FILE"

# Upload the preprocessed file and FastQC report to S3
aws s3 cp /data/ "$OUTPUT_S3_PATH" --recursive
