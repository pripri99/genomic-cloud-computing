import os
import subprocess
import boto3

def download_file(bucket, key, filename):
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, filename)

def upload_file(bucket, key, filename):
    s3 = boto3.client('s3')
    s3.upload_file(filename, bucket, key)

def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()

def align_reads(reference_genome_name, input_file_name, output_bucket, output_key):
    reference_bucket = 'alucloud76-genomic'
    reference_key = f'dataset/{reference_genome_name}.fasta'
    fastq_bucket = 'alucloud76-genomic'

    # Download files from S3
    download_file(reference_bucket, reference_key, 'reference.fasta')
    download_file(fastq_bucket, input_file_name, 'reads.fastq')

    # Index the reference genome
    run_command('bwa index reference.fasta')

    # Align reads and convert to BAM
    output_file_name = 'align/' + input_file_name.split('/')[-1].split('.')[0] + '_aligned.bam'
    run_command(f'bwa mem reference.fasta reads.fastq | samtools view -bS - > {output_file_name}')

    # Upload output to S3
    upload_file(output_bucket, output_key + '/' + output_file_name, output_file_name)


if __name__ == "__main__":
    import sys
    input_bucket = 'alucloud76-genomic'
    input_prefix = 'preprocessed/'

    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=input_bucket, Prefix=input_prefix)

    for obj in response['Contents']:
        if obj['Key'].endswith('.fastq'):
            input_file_name = obj['Key']
            output_key = 'align/' + input_file_name.split('/')[1].split('.')[0] + '_aligned.bam'
            align_reads(sys.argv[1], input_file_name, sys.argv[2], output_key)

    # Example on how to use this file
    # python aligner.py SARS-CoV-2 SRR24441101 alucloud76-genomic align/SRR24441101_aligned.bam
    # where dataset/SARS-CoV-2.fasta and preprocessed/SRR24441101_preprocessed.fastq are both inside the bucket alucloud76-genomic


