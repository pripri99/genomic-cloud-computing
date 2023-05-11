# Use Bioconda base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Install required tools using Bioconda
RUN conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda install -y fastqc trimmomatic bwa samtools awscli

# Create a directory for the Trimmomatic adapter files
RUN mkdir -p /usr/local/share/trimmomatic/adapters/

# Download the Trimmomatic adapter files
RUN wget -P /usr/local/share/trimmomatic/adapters/ http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.39-1.zip && \
    unzip /usr/local/share/trimmomatic/adapters/Trimmomatic-0.39-1.zip -d /usr/local/share/trimmomatic/adapters/ && \
    rm /usr/local/share/trimmomatic/adapters/Trimmomatic-0.39-1.zip

# Copy your preprocessing script into the container
COPY preprocess.sh /app

# Make the script executable
RUN chmod +x /app/preprocess.sh

# Set the entrypoint to run the preprocessing script
ENTRYPOINT ["/app/preprocess.sh"]
