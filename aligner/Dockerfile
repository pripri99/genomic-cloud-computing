FROM python:3.8-slim-buster

# Install dependencies and build tools
RUN apt-get update && \
    apt-get install -y wget libncurses5-dev zlib1g-dev libbz2-dev liblzma-dev bzip2 build-essential libcurl4-openssl-dev

# Install BWA
RUN wget https://github.com/lh3/bwa/releases/download/v0.7.17/bwa-0.7.17.tar.bz2 && \
    tar -xvf bwa-0.7.17.tar.bz2 && \
    cd bwa-0.7.17 && \
    make && \
    cp bwa /usr/local/bin

# Install SAMtools
RUN wget https://github.com/samtools/samtools/releases/download/1.17/samtools-1.17.tar.bz2 && \
    tar -xvf samtools-1.17.tar.bz2 && \
    cd samtools-1.17 && \
    make && \
    cp samtools /usr/local/bin

# Install AWS CLI and Boto3
RUN pip install awscli boto3

# Create the align folder in the image
RUN mkdir /align

# Copy Python script into image
COPY aligner.py /aligner.py

# Set Python script as entrypoint
# ENTRYPOINT ["python", "/aligner.py"]
