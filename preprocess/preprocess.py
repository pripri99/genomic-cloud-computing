import os
import logging
import boto3
import gzip
from botocore.exceptions import NoCredentialsError
from Bio import SeqIO
from io import StringIO
import datetime

log_bucket_name = 'logging-genomics'
log_file_key = 'app.log'

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def download_and_unzip_s3_file(bucket_name, file_key):
    s3 = boto3.client('s3')

    try:
        print("Key is:", file_key)
        s3_object = s3.get_object(Bucket=bucket_name, Key=file_key)
        gzipped_data = s3_object['Body'].read()
        uncompressed_data = gzip.decompress(gzipped_data)

        local_input_file = file_key.split("/")[-1]

        with open(local_input_file, 'wb') as output_file:
            output_file.write(uncompressed_data)
        
        print(f"Loaded data from s3://{bucket_name}/{file_key}")

    except NoCredentialsError:
        print("Error: Unable to access S3 bucket. Check your AWS credentials.")
    except Exception as e:
        print(f"Error: {e}")
    
    return local_input_file

def is_high_quality(record, min_quality):
    try:
        quality_scores = record.letter_annotations['phred_quality']
        average_quality = sum(quality_scores) / len(quality_scores)
        #print("scores:", quality_scores, "average:", average_quality)
        return average_quality >= min_quality
    except Exception as e:
            logging.error(f"Error in is_high_quality: {e}")

def preprocess_fastq_data(input_file, min_quality=20, local_output='output.fastq', output_file='preprocessed/output.fastq', output_bucket_name="alucloud76-genomic", log_file='preprocessing_log.txt'):
    # Filter reads based on minimum quality

    high_quality_reads = []
    total_reads = 0
    low_quality_reads = 0

    with open(input_file, 'rt') as input_handle:
        for record in SeqIO.parse(input_handle, 'fastq'):
            total_reads += 1
            if is_high_quality(record, min_quality):
                high_quality_reads.append(record)
            else:
                low_quality_reads += 1

    with open(local_output, 'wt') as output_handle:
        SeqIO.write(high_quality_reads, output_handle, 'fastq')

    # Log the percentage of high and low-quality sequences
    high_quality_percentage = (len(high_quality_reads) / total_reads) * 100
    low_quality_percentage = (low_quality_reads / total_reads) * 100

    now = datetime.datetime.now()
    log_message = f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Preprocessed data saved to s3://{output_bucket_name}/{output_file}\n'
    log_message += f'{now.strftime("%Y-%m-%d %H:%M:%S")} - High quality sequences: {high_quality_percentage:.2f}%\n'
    log_message += f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Low quality sequences: {low_quality_percentage:.2f}%\n'

    with open(log_file, 'a') as log_handle:
        log_handle.write(log_message)
    
    # Write the high quality reads to a StringIO object
    output_data = StringIO()
    SeqIO.write(high_quality_reads, output_data, 'fastq')

    print("NOW SAVING THE PREPROCESSED DATA")
    # Upload the output file and log file to S3
    s3 = boto3.client('s3')
    output_data.seek(0)
    s3.put_object(Bucket=output_bucket_name, Key=f'{output_file}', Body=output_data.read().encode('utf-8'), ContentType='text/plain', ACL='bucket-owner-full-control')
    # s3.put_object(Bucket=output_bucket_name, Key=f'{log_file}', Body=log_message.encode('utf-8'), ContentType='text/plain', ACL='bucket-owner-full-control')

    print(f'Preprocessed data saved to s3://{output_bucket_name}/{output_file}')

    return log_message


def upload_log_to_s3(bucket_name, file_key, file_path):
    s3 = boto3.client('s3')
    try:
        with open(file_path, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, file_key)
        print(f"Log file saved to s3://{bucket_name}/{file_key}")
    except Exception as e:
        print(f"Error uploading log file: {e}")


def get_all_fastq_files(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    fastq_files = []
    
    for obj in bucket.objects.all():
        if obj.key.endswith('.fastq.gz'):
            fastq_files.append(obj.key)
    
    return fastq_files

if __name__ == '__main__':
    print("hello let's start")
    try:
        bucket_name = os.environ.get('INPUT_BUCKET_NAME', 'alucloud76-genomic')
        output_bucket_name = os.environ.get('OUTPUT_BUCKET_NAME', 'alucloud76-genomic')

        all_fastq_files = get_all_fastq_files(bucket_name)
        log_data = ""

        for file_key in all_fastq_files:
            input_folder_name = "dataset/"
            output_folder_name = "preprocessed/"
            print(bucket_name, output_bucket_name, file_key)

            local_input_file = download_and_unzip_s3_file(bucket_name, file_key)
            output_file_name = file_key.replace('.fastq.gz', '_preprocessed.fastq').replace(input_folder_name, output_folder_name)
            print("output_file_name: ",output_file_name)
            log_data += preprocess_fastq_data(local_input_file, output_file=output_file_name, output_bucket_name=output_bucket_name)

        print("To Finish Saving The log")
        print(log_data)
        s3 = boto3.client('s3')
        s3.put_object(Bucket=output_bucket_name, Key="preprocessing_log.txt", Body=log_data.encode('utf-8'), ContentType='text/plain', ACL='bucket-owner-full-control')
            
    except Exception as e:
        print(e)
        logging.error(f"Error in main execution: {e}")
    
    # After all processing, upload the log file to S3
    # upload_log_to_s3(log_bucket_name, log_file_key, 'app.log')
