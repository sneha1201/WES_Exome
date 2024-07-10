#!/usr/bin/env python
# coding: utf-8

import os
import sys
import subprocess

# Function to check if a tool is installed
def is_tool_installed(tool):
    return subprocess.call(['which', tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

# Function to install necessary tools using subprocess
def install_tools():
    if not is_tool_installed('fastqc'):
        subprocess.run(['brew', 'install', 'fastqc'])  # Install FastQC using brew
    if not is_tool_installed('bwa'):
        subprocess.run(['brew', 'install', 'bwa'])  # Install BWA using brew
    if not is_tool_installed('samtools'):
        subprocess.run(['brew', 'install', 'samtools'])  # Install SAMtools using brew
    if not is_tool_installed('bcftools'):
        subprocess.run(['brew', 'install', 'bcftools'])  # Install BCFtools using brew

# Function to index the reference genome using BWA
def index_reference_genome(reference_genome):
    subprocess.run(['bwa', 'index', reference_genome])  # Index the reference genome

# Function to run FastQC on input FASTQ files
def run_fastqc(fastq_files):
    for fastq in fastq_files:
        subprocess.run(['fastqc', fastq])  # Run FastQC for each input file

# Function to align reads to the reference genome using BWA
def align_reads(reference_genome, fastq_files):
    for fastq in fastq_files:
        if '_R1.fastq.gz' in fastq:
            fastq_r2 = fastq.replace('_R1.fastq.gz', '_R2.fastq.gz')
            if not os.path.exists(fastq_r2):
                print(f"Error: Paired file {fastq_r2} not found for {fastq}")
                sys.exit(1)
            output_sam = fastq.replace('_R1.fastq.gz', '.sam')  # Output SAM file
            command = f"bwa mem {reference_genome} <(gunzip -c {fastq}) <(gunzip -c {fastq_r2}) > {output_sam}"
            result = subprocess.run(command, shell=True, executable='/bin/bash')
            if result.returncode != 0:
                print(f"Error aligning reads for {fastq}")
                sys.exit(1)
        else:
            print(f"Skipping non-R1 file: {fastq}")

# Function to convert SAM to BAM, sort, and index using SAMtools
def process_alignment(sam_files):
    for sam_file in sam_files:
        output_bam = sam_file.replace('.sam', '.bam')  # Output BAM file
        output_sorted_bam = output_bam.replace('.bam', '_sorted.bam')  # Output sorted BAM file
        subprocess.run(['samtools', 'view', '-S', '-b', sam_file, '-o', output_bam])  # Convert SAM to BAM
        subprocess.run(['samtools', 'sort', '-o', output_sorted_bam, output_bam])  # Sort BAM file
        subprocess.run(['samtools', 'index', output_sorted_bam])  # Index sorted BAM file

# Function to call variants using BCFtools
def call_variants(reference_genome, sorted_bams):
    for sorted_bam in sorted_bams:
        output_vcf = sorted_bam.replace('_sorted.bam', '.vcf')  # Output VCF file
        command = f"bcftools mpileup -Ou -f {reference_genome} {sorted_bam} | bcftools call -mv -o {output_vcf}"
        result = subprocess.run(command, shell=True, executable='/bin/bash')
        if result.returncode != 0:
            print(f"Error calling variants for {sorted_bam}")
            sys.exit(1)

# Function to log each step's output to a log file
def log_output(step_name, output):
    with open('pipeline.log', 'a') as log_file:
        log_file.write(f'{step_name}:\n{output}\n\n')

if __name__ == "__main__":
    # Check and install necessary tools if not already installed
    install_tools()

    # Get the folder containing FASTQ files as argument
    fastq_folder = sys.argv[1]

    # Constant reference genome file
    reference_genome = "reference.fasta"

    # Get list of FASTQ files in the folder
    fastq_files = [os.path.join(fastq_folder, f) for f in os.listdir(fastq_folder) if f.endswith('.fastq.gz')]

    # Check if there are any FASTQ files
    if not fastq_files:
        print("Error: No FASTQ files found in the specified folder.")
        sys.exit(1)

    # Index the reference genome
    print("Indexing the reference genome...")
    index_reference_genome(reference_genome)
    log_output('Reference Genome Indexing', 'Reference genome indexing completed successfully')

    # Run FastQC on input FASTQ files
    print("Running FastQC on input FASTQ files...")
    run_fastqc(fastq_files)
    log_output('FastQC', 'FastQC completed successfully')

    # Align reads to the reference genome using BWA
    print("Aligning reads to the reference genome...")
    align_reads(reference_genome, fastq_files)
    log_output('BWA Alignment', 'BWA alignment completed successfully')

    # Get list of generated SAM files
    sam_files = [f.replace('_R1.fastq.gz', '.sam') for f in fastq_files if '_R1.fastq.gz' in f]

    # Process alignment (convert SAM to BAM, sort, and index)
    print("Processing alignment (SAM to BAM, sorting, and indexing)...")
    process_alignment(sam_files)
    log_output('SAM to BAM Conversion', 'SAM to BAM conversion completed successfully')

    # Get list of sorted BAM files
    sorted_bams = [f.replace('.sam', '_sorted.bam') for f in sam_files]

    # Call variants using BCFtools
    print("Calling variants using BCFtools...")
    call_variants(reference_genome, sorted_bams)
    log_output('Variant Calling', 'Variant calling completed successfully')
